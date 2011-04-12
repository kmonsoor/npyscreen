#!/usr/bin/python
from . import wgmultiline    as multiline
from . import wgtextbox      as textbox
from . import wgcheckbox     as checkbox
from . import wgselectone    as selectone
from . import npysNPSTree    as NPSTree
import curses
import weakref


class TreeLine(textbox.TextfieldBase):
    def __init__(self, *args, **keywords):
        self._tree_real_value   = None
        self._tree_ignore_root  = None
        self._tree_depth        = False
        self._tree_sibling_next = False
        self._tree_has_children = False
        self._tree_expanded     = True
        self._tree_last_line    = False
        self._tree_depth_next   = False
        self.safe_depth_display = False
        self.show_v_lines       = False
        super(TreeLine, self).__init__(*args, **keywords)
        
    #EXPERIMENTAL
    def _print(self):
        self.left_margin = 0
        self.parent.curses_pad.bkgdset(' ',curses.A_NORMAL)
        self.left_margin += self._print_tree(self.relx)
        if self.highlight:
            self.parent.curses_pad.bkgdset(' ',curses.A_STANDOUT)
        super(TreeLine, self)._print()
        
    def _print_tree(self, real_x):
        if hasattr(self._tree_real_value, 'findDepth'):
            control_chars_added = 0
            this_safe_depth_display = self.safe_depth_display or ((self.width // 2) + 1)
            if self._tree_depth_next:
                _tree_depth_next = self._tree_depth_next
            else:
                _tree_depth_next = 0
            dp = self._tree_depth
            if self._tree_ignore_root:
                dp -= 1
            if dp: # > 0:
                if dp < this_safe_depth_display:                    
                    for i in range(dp-1):
                        if (i < _tree_depth_next) and (not self._tree_last_line) and not (_tree_depth_next==1):
                            if self.show_v_lines:
                                self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_VLINE, curses.A_NORMAL)
                            else:
                                self.parent.curses_pad.addch(self.rely, real_x, ' ', curses.A_NORMAL)
                                
                        else:
                            if self.show_v_lines:
                                self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_BTEE, curses.A_NORMAL)
                            else:
                                self.parent.curses_pad.addch(self.rely, real_x, ' ', curses.A_NORMAL)
                                
                        real_x +=1
                        self.parent.curses_pad.addch(self.rely, real_x, ord(' '), curses.A_NORMAL)
                        real_x +=1
                    
                    
                    
                    if self._tree_sibling_next:
                        self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_LTEE, curses.A_NORMAL)
                    else:
                        self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_LLCORNER, curses.A_NORMAL)
                    real_x += 1
                    self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_HLINE, curses.A_NORMAL)
                    real_x += 1
                else:
                    self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_HLINE, curses.A_NORMAL)
                    real_x += 1
                    self.parent.curses_pad.addstr(self.rely, real_x, "[ %s ]" % (str(dp)), curses.A_NORMAL)
                    real_x += len(str(dp)) + 4
                    self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_RTEE, curses.A_NORMAL)
                    real_x += 1
                    
            if self._tree_has_children:
                if self._tree_expanded:
                    self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_TTEE, curses.A_NORMAL)
                else:   
                    self.parent.curses_pad.addch(self.rely, real_x, curses.ACS_RARROW, curses.A_NORMAL)
                real_x +=1
            else:
                real_x +=1
            control_chars_added += real_x - self.relx
            margin_needed = control_chars_added + 1
        else:
            margin_needed = 0
        return margin_needed
        
        
    def display_value(self, vl):
        try:
            return self.safe_string(vl.getContent())
        except:
            # Catch the times this is None.
            return self.safe_string(vl)
            
    

class TreeLineAnnotated(TreeLine):
    ## Experimental.
    _annotate = "   ?   "
    _annotatecolor = 'CONTROL'
    def setAnnotateString(self):
        self._annotate = "   ?   "
        self._annotatecolor = 'CONTROL'
    
    def annotationColor(self, real_x):
        # Must return the "Margin" needed before the entry begins
        self.setAnnotateString()
        self.parent.curses_pad.addstr(self.rely, real_x, self._annotate, self.parent.theme_manager.findPair(self, self._annotatecolor))
        return len(self._annotate)
        
    def annotationNoColor(self, real_x):
        # Must return the "Margin" needed before the entry begins
        #self.parent.curses_pad.addstr(self.rely, real_x, 'xxx')
        #return 3
        self.setAnnotateString()
        self.parent.curses_pad.addstr(self.rely, real_x, self._annotate)
        return len(self._annotate)
    
    def _print(self):
        self.left_margin = 0
        self.parent.curses_pad.bkgdset(' ',curses.A_NORMAL)
        self.left_margin += self._print_tree(self.relx)
        if self.do_colors():    
            self.left_margin += self.annotationColor(self.left_margin+self.relx)
        else:
            self.left_margin += self.annotationNoColor(self.left_margin+self.relx)
        if self.highlight:
            self.parent.curses_pad.bkgdset(' ',curses.A_STANDOUT)
        super(TreeLine, self)._print()


class MultiLineTreeNew(multiline.MultiLine):
    # Experimental
    _contained_widgets = TreeLineAnnotated
    def _setMyValues(self, tree):
        if tree == [] or tree == None:
            self._myFullValues = NPSTree.NPSTreeData()
        elif not isinstance(tree, NPSTree.NPSTreeData):
            raise TypeError("MultiLineTree widget can only contain a NPSTreeData object in its values attribute")
        else:
            self._myFullValues = tree
            
    def clearDisplayCache(self):
        self._cached_tree = None
        self._cached_sort = None
        self._cached_tree_as_list = None
    
    def _getApparentValues(self):
        try:
            if self._cached_tree is weakref.proxy(self._myFullValues) and \
            (self._cached_sort == (self._myFullValues.sort, self._myFullValues.sort_function)):
                return self._cached_tree_as_list
        except:
            pass
        self._cached_tree = weakref.proxy(self._myFullValues)
        self._cached_sort = (self._myFullValues.sort, self._myFullValues.sort_function)
        self._cached_tree_as_list = self._myFullValues.getTreeAsList()
        return self._cached_tree_as_list
    
    def _walkMyValues(self):
        return self._myFullValues.walkTree()
    
    def _delMyValues(self):
        self._myFullValues = None
    
    values = property(_getApparentValues, _setMyValues, _delMyValues)
    
    def filter_value(self, index):
        if self._filter in self.display_value(self.values[index].getContent()):
            return True
        else:
            return False
    
    
    def set_up_handlers(self):
        super(MultiLineTreeNew, self).set_up_handlers()
        self.handlers.update({
                ord('<'): self.h_collapse_tree,
                ord('>'): self.h_expand_tree,
                ord('['): self.h_collapse_tree,
                ord(']'): self.h_expand_tree,
                ord('{'): self.h_collapse_all,
                ord('}'): self.h_expand_all,                
        })

    
    
    #def display_value(self, vl):
    #    return vl
    
    def _set_line_values(self, line, value_indexer):
        line._tree_real_value   = None
        line._tree_depth        = False
        line._tree_sibling_next = False
        line._tree_has_children = False
        line._tree_expanded     = False
        line._tree_last_line    = False
        line._tree_depth_next   = False
        line._tree_ignore_root  = None
        try:
            line.value = self.display_value(self.values[value_indexer])
            line._tree_real_value = self.values[value_indexer]
            line._tree_ignore_root = self._myFullValues.ignoreRoot
            try:
                line._tree_depth        = self.values[value_indexer].findDepth()
                line._tree_has_children = self.values[value_indexer].hasChildren()
                line._tree_expanded     = self.values[value_indexer].expanded
            except:
                line._tree_depth        = False
                line._tree_has_children = False
                line._tree_expanded     = False
            try:
                if line._tree_depth == self.values[value_indexer+1].findDepth():
                    line._tree_sibling_next = True
                else:
                    line._tree_sibling_next = False
            except:
                line._sibling_next = False
                line._tree_last_line = True
            try:
                line._tree_depth_next = self.values[value_indexer+1].findDepth()
            except:
                line._tree_depth_next = False
            line.hide = False
        except IndexError:
            self._set_line_blank(line)
        except TypeError:
            self._set_line_blank(line)
            
    def h_collapse_tree(self, ch):
        if self.values[self.cursor_line].expanded and self.values[self.cursor_line].hasChildren():
            self.values[self.cursor_line].expanded = False
        else:
            look_for_depth = self.values[self.cursor_line].findDepth() - 1
            cursor_line = self.cursor_line - 1
            while cursor_line >= 0:
                if look_for_depth == self.values[cursor_line].findDepth():
                    self.cursor_line = cursor_line
                    self.values[cursor_line].expanded = False
                    break
                else:
                    cursor_line -=1
        self._cached_tree = None
        self.display()

    def h_expand_tree(self, ch):
        if not self.values[self.cursor_line].expanded:
            self.values[self.cursor_line].expanded = True
        else:
            for v in self.values[self.cursor_line].walkTree(onlyExpanded=False):
                v.expanded = True
        self._cached_tree = None
        self.display()
    
    def h_collapse_all(self, ch):
        for v in self._myFullValues.walkTree(onlyExpanded=True):
            v.expanded = False
        self._cached_tree = None
        self.cursor_line = 0
        self.display()
    
    def h_expand_all(self, ch):
        for v in self._myFullValues.walkTree(onlyExpanded=False):
            v.expanded    = True
        self._cached_tree = None
        self.cursor_line  = 0
        self.display()



class MultiLineTreeNewAction(MultiLineTreeNew, multiline.MultiLineAction):
    pass
#    # Copied from the above.  
#    _contained_widgets = TreeLineAnnotated
#    def _setMyValues(self, tree):
#        if tree == [] or tree == None:
#            self._myFullValues = NPSTree.NPSTreeData()
#        elif not isinstance(tree, NPSTree.NPSTreeData):
#            raise TypeError("MultiLineTree widget can only contain a NPSTreeData object in its values attribute")
#        else:
#            self._myFullValues = tree
#    
#    def _getApparentValues(self):
#        try:
#            if self._cached_tree == weakref.proxy(self._myFullValues):
#                return self._cached_tree_as_list
#        except:
#            pass
#        self._cached_tree = weakref.proxy(self._myFullValues)
#        self._cached_tree_as_list = self._myFullValues.getTreeAsList()
#        return self._cached_tree_as_list
#    
#    def _walkMyValues(self):
#        return self._myFullValues.walkTree()
#    
#    def _delMyValues(self):
#        self._myFullValues = None
#    
#    values = property(_getApparentValues, _setMyValues, _delMyValues)
#    
#    #def display_value(self, vl):
#    #    return vl
#    
#    def _set_line_values(self, line, value_indexer):
#        line._tree_real_value   = None
#        line._tree_depth        = False
#        line._tree_sibling_next = False
#        line._tree_has_children = False
#        line._tree_expanded     = False
#        line._tree_last_line    = False
#        line._tree_depth_next   = False
#        
#        try:
#            line.value = self.display_value(self.values[value_indexer])
#            line._tree_real_value = self.values[value_indexer]
#            line._tree_ignore_root = self._myFullValues.ignoreRoot
#            
#            try:
#                line._tree_depth        = self.values[value_indexer].findDepth()
#                line._tree_has_children = self.values[value_indexer].hasChildren()
#                line._tree_expanded     = self.values[value_indexer].expanded
#            except:
#                line._tree_depth        = False
#                line._tree_has_children = False
#                line._tree_expanded     = False
#            try:
#                if line._tree_depth == self.values[value_indexer+1].findDepth():
#                    line._tree_sibling_next = True
#                else:
#                    line._tree_sibling_next = False
#            except:
#                line._sibling_next = False
#                line._tree_last_line = True
#            try:
#                line._tree_depth_next = self.values[value_indexer+1].findDepth()
#            except:
#                line._tree_depth_next = False
#        
#            line.hide = False
#        except IndexError:
#            self._set_line_blank(line)
#        except TypeError:
#            self._set_line_blank(line)
#    






# OLD TREE WIDGET


class MultiLineTree(multiline.MultiLine):
    def _setMyValues(self, tree):
        if tree == [] or tree == None:
            self._myFullValues = NPSTree.NPSTreeData()
        elif not isinstance(tree, NPSTree.NPSTreeData):
            raise TypeError("MultiLineTree widget can only contain a NPSTreeData object in its values attribute")
        else:
            self._myFullValues = tree
    
    def _getApparentValues(self):
        return self._myFullValues.getTreeAsList()
    
    def _walkMyValues(self):
        return self._myFullValues.walkTree()
    
    def _delMyValues(self):
        self._myFullValues = None
    
    values = property(_getApparentValues, _setMyValues, _delMyValues)
    
    def get_tree_display(self, vl):
        dp = vl.findDepth()
        if dp > 0:
            control_chars = "| " * (dp-1) + "|-"
        else:
            control_chars = ""
        if vl.hasChildren():
            if vl.expanded:
                control_chars = control_chars + "+"
            else:   
                control_chars = control_chars + ">"
        else:
            control_chars = control_chars + ""
        return control_chars
    
    def _set_line_values(self, line, value_indexer):
        try:
            line.value = self.get_tree_display(self.values[value_indexer]) + "  " + self.display_value(self.values[value_indexer]) + "  "
            line.hide = False
        except IndexError:
            self._set_line_blank(line)
        except TypeError:
            self._set_line_blank(line)
    
    def display_value(self, vl):
        return str(vl.getContentForDisplay()) 
    
class SelectOneTree(MultiLineTree):
    _contained_widgets = checkbox.RoundCheckBox
    def _print_line(self, line, value_indexer):
        try:
            line.value = self.values[value_indexer]
            line.hide = False
            if (self.values[value_indexer] in self.value and (self.value is not None)):
                line.show_bold = True
                line.name = self.display_value(self.values[value_indexer])
                line.value = True
            else:
                line.show_bold = False
                line.name = self.display_value(self.values[value_indexer])
                line.value = False
            if value_indexer in self._filtered_values_cache:
                line.important = True
            else:
                line.important = False
        except IndexError:
            line.name = None
            line.hide = True

        line.highlight= False
    
    def update(self, clear=True):
        if self.hidden and clear:
            self.clear()
            return False
        elif clear:
            return False
        # Make sure that self.value is a list
        if not hasattr(self.value, "append"):
            if self.value is not None:
                self.value = [self.value, ]
            else:
                self.value = []

        super(SelectOneTree, self).update(clear=clear)

    def h_select(self, ch):
        try:
            self.value = [weakref.proxy(self.values[self.cursor_line]),]
        except TypeError:
            # Actually, this is inefficient, since with the NPSTree class (default) we will always be here - since by default we will 
            # try to create a weakref to a weakref, and that will fail with a type-error.  BUT we are only doing it on a keypress, so
            # it shouldn't create a huge performance hit, and is future-proof. Code replicated in h_select_exit
            self.value = [self.values[self.cursor_line],]
    
    def h_select_exit(self, ch):
        try:
            self.value = [weakref.proxy(self.values[self.cursor_line]),]
        except TypeError:
            # Actually, this is inefficient, since with the NPSTree class (default) we will always be here - since by default we will 
            # try to create a weakref to a weakref, and that will fail with a type-error.  BUT we are only doing it on a keypress, so
            # it shouldn't create a huge performance hit, and is future-proof.
            self.value = [self.values[self.cursor_line],]
        if self.return_exit:
            self.editing = False
            self.how_exited=True
            
    def h_set_filtered_to_selected(self, ch):
        if len(self._filtered_values_cache) < 2:
            self.value = self.get_filtered_values()
        else:
            # There is an error - trying to select too many things.
            curses.beep()

        




