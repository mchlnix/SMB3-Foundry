import wx.lib.newevent

JumpListUpdate, EVT_JUMP_LIST = wx.lib.newevent.NewCommandEvent()

ObjectListUpdateEvent, EVT_OBJ_LIST = wx.lib.newevent.NewCommandEvent()
ObjectsSelectedEvent, EVT_OBJ_SELECT = wx.lib.newevent.NewCommandEvent()

UndoEvent, EVT_UNDO = wx.lib.newevent.NewCommandEvent()
RedoEvent, EVT_REDO = wx.lib.newevent.NewCommandEvent()

UndoCompleteEvent, EVT_UNDO_COMPLETE = wx.lib.newevent.NewCommandEvent()
RedoCompleteEvent, EVT_REDO_COMPLETE = wx.lib.newevent.NewCommandEvent()

UndoStateSavedEvent, EVT_UNDO_SAVED = wx.lib.newevent.NewCommandEvent()
UndoStackClearedEvent, EVT_UNDO_CLEARED = wx.lib.newevent.NewCommandEvent()
