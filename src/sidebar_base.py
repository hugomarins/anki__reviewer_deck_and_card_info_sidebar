import aqt 
from aqt.qt import (
    QCursor,
    QDockWidget,
    QMenu,
    QPalette,
    QSize,
    Qt,
    pyqtSignal,
)
from anki.hooks import addHook
from aqt.webview import AnkiWebView
from aqt.utils import tooltip

from .anki_version_detection import anki_point_version
from .config import anki_21_version, gc
from .sidebar_set_contents import update_contents_of_sidebar


class ThinAnkiWebView(AnkiWebView):
    def __init__(self, sidebar):
        AnkiWebView.__init__(self, None)
        self.sidebar = sidebar
    def sizeHint(self):
        return QSize(gc("default width", 200), 100)
    # def contextMenuEvent(self, evt):
    #     m = QMenu(self)
    #     a = m.addAction("Hello")
    #     a.triggered.connect(self.sidebar.on_hello)
    #     m.popup(QCursor.pos())


class DockableWithClose(QDockWidget):
    closed = pyqtSignal()
    def closeEvent(self, evt):
        self.closed.emit()
        QDockWidget.closeEvent(self, evt)


class StatsSidebar:
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        self.night_mode_on = False
        if mw.pm.night_mode():
            self.night_mode_on = True
        addHook("showQuestion", lambda: update_contents_of_sidebar(self))
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)
        addHook("night_mode_state_changed", self.refresh)
        if anki_point_version >= 50:
            aqt.gui_hooks.theme_did_change.append(self.setup_style)
    
    def setup_style(self):  # theme change in Anki - only in .50+
        if self.shown:
            if aqt.theme.theme_manager.get_night_mode():  # if self.night_mode_on:
                self.set_dark_style()
            else:
                self.set_day_style()

    def set_dark_style(self):
        # https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qdockwidget
        # I think I can't style the divider since this like a window border which are
        # owned by the OS?
        # A QSplitter can be styled but I think this would require to
        # change main.py/setupMainWindow which I don't want to do.
        bgcolor = QPalette().window().color().name()
        if self.shown:
            self.shown.setStyleSheet("""
            QWidget::title {
                color: white;
                background-color: #272828;
            }
            """)
            update_contents_of_sidebar(self)

    def set_day_style(self):
        bgcolor = QPalette().window().color().name()
        if self.shown:
            self.shown.setStyleSheet("")
            update_contents_of_sidebar(self)

    def refresh(self, nm_state):
        self.night_mode_on=nm_state
        if self.shown:
            self._remDockable(self.shown)
        self.shown = None
        if self.mw.state == "review":
            self.show()
        
    def _addDockable(self, title, w):
        dock = DockableWithClose(title, self.mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        dock.setWidget(w)
        if self.mw.width() < 600:
            self.mw.resize(QSize(600, self.mw.height()))
        self.mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        if anki_point_version <= 49:
            if aqt.theme.theme_manager.get_night_mode():  # if self.night_mode_on:
                # https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qdockwidget
                # I think I can't style the divider since this like a window border which are
                # owned by the OS?
                # A QSplitter can be styled but I think this would require to
                # change main.py/setupMainWindow which I don't want to do.
                dock.setStyleSheet("""
                QWidget::title {
                    color: white;
                    background-color: #272828;
                }
                """)
        return dock

    def _remDockable(self, dock):
        if anki_point_version >= 50:
            aqt.gui_hooks.theme_did_change.remove(self.setup_style)
        self.mw.removeDockWidget(dock)

    def show(self):
        if not self.shown:
            self.web = ThinAnkiWebView(self)
            self.shown = self._addDockable("", self.web)
            if anki_point_version >= 50:
                self.setup_style()
            self.shown.closed.connect(self._onClosed)
            self.web.onBridgeCmd = self.myLinkHandler
        update_contents_of_sidebar(self)

    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None

    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()

    def _onClosed(self):
        # schedule removal for after evt has finished
        self.mw.progress.timer(100, self.hide, False)
    
    def myLinkHandler(self, url):
        if url.startswith("BrowserSearch#"):
            out = url.replace("BrowserSearch#", "").split("#", 1)[0]
            self.openBrowser("cid:" + out)
            
    def openBrowser(self, searchterm):
        # https://ankiweb.net/shared/info/861864770
        # Open 'Added Today' from Reviewer
        # Copyright (c) 2013 Steve AW
        # Copyright (c) 2016-2017 Glutanimate
        browser = aqt.dialogs.open("Browser", self.mw)
        browser.form.searchEdit.lineEdit().setText(searchterm)
        browser.onSearchActivated()
        if anki_21_version < 45:
            if u'noteCrt' in browser.model.activeCols:
                col_index = browser.model.activeCols.index(u'noteCrt')
                browser.onSortChanged(col_index, True)
            browser.form.tableView.selectRow(0)  
        else:
            pass
