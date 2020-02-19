import aqt 
from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.webview import AnkiWebView
from anki.lang import _

from .sidebar_set_contents import update_contents_of_sidebar


class StatsSidebar(object):
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        self.night_mode_on = False
        addHook("showQuestion", lambda: update_contents_of_sidebar(self))
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)
        addHook("night_mode_state_changed", self.refresh)

    def refresh(self, nm_state):
        self.night_mode_on=nm_state
        if self.shown:
            self._remDockable(self.shown)
        self.shown = None
        if self.mw.state == "review":
            self.show()
        
    def _addDockable(self, title, w):
        class DockableWithClose(QDockWidget):
            closed = pyqtSignal()
            def closeEvent(self, evt):
                self.closed.emit()
                QDockWidget.closeEvent(self, evt)
        dock = DockableWithClose(title, self.mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable)
        dock.setWidget(w)
        if self.mw.width() < 600:
            self.mw.resize(QSize(600, self.mw.height()))
        self.mw.addDockWidget(Qt.RightDockWidgetArea, dock)
        if self.night_mode_on:
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
        self.mw.removeDockWidget(dock)

    def show(self):
        if not self.shown:
            class ThinAnkiWebView(AnkiWebView):
                def __init__(self, sidebar):
                    AnkiWebView.__init__(self, None)
                    self.sidebar = sidebar
                def sizeHint(self):
                    return QSize(200, 100)
                # def contextMenuEvent(self, evt):
                #     m = QMenu(self)
                #     a = m.addAction(_("Toggle Dark Mode"))
                #     a.triggered.connect(self.sidebar.onDarkMode)
                #     m.popup(QCursor.pos())
            self.web = ThinAnkiWebView(self)
            self.shown = self._addDockable("", self.web)
            self.shown.closed.connect(self._onClosed)
            self.web.onBridgeCmd = self.myLinkHandler
        update_contents_of_sidebar(self)

    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None
            mw.sidebar673114053visibility = True
        else:
            mw.sidebar673114053visibility = False

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
        if u'noteCrt' in browser.model.activeCols:
            col_index = browser.model.activeCols.index(u'noteCrt')
            browser.onSortChanged(col_index, True)
        browser.form.tableView.selectRow(0)  
