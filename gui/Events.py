import wx.lib.newevent

UndoEvent, EVT_UNDO = wx.lib.newevent.NewCommandEvent()
RedoEvent, EVT_REDO = wx.lib.newevent.NewCommandEvent()

UndoCompleteEvent, EVT_UNDO_COMPLETE = wx.lib.newevent.NewCommandEvent()
RedoCompleteEvent, EVT_REDO_COMPLETE = wx.lib.newevent.NewCommandEvent()

UndoStackClearedEvent, EVT_UNDO_CLEARED = wx.lib.newevent.NewCommandEvent()

UndoStateSavedEvent, EVT_UNDO_SAVED = wx.lib.newevent.NewCommandEvent()
