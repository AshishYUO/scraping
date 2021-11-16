#!/usr/bin/env python
import json

class Node:
    """
    Node to store the history of data search
    """
    def __init__(self, data):
        self.data = data
        self.NextData = None
        self.PreviousData = None

class HistoryList:
    """
    History List stores the history of n previous searches, defaults to 10
    Maintains in a form of doubly linked list, and deletes nth query from Head
    (if limit size is n)
    """
    def __init__(self, MaxSize=10):
        self.Head = None
        self.Tail = None
        self.MaxSize = MaxSize
        self.Size = 0

    def __iadd__(self, data):
        """
        :details Add the next data onto the list
        operator is historyList += data
        :param data: json/dictionary
        :returns this
        """
        # trivial case: if list is empty
        if self.Head is None and self.Tail is None:
            self.Head = self.Tail = Node(data)
        # else add to the Tail of the list
        else:
            # if size is at the limit, remove the Head and set the next node as 
            # new Head
            if self.Size == 10:
                TempReference = self.Head
                self.Head = self.Head.NextData
                self.Head.PreviousData = None
                del TempReference
                self.Size -= 1
            # add to the list
            NewData = Node(data)
            self.Tail.NextData = NewData
            NewData.PreviousData = self.Tail
            self.Tail = NewData
            self.Size += 1

        return self

    def __str__(self):
        """
        String representation of the HistoryList
        """
        Traverse = self.Tail
        index = 0
        display = "Recent History Size: %d\n" % self.Size
        while Traverse is not None:
            display += '%d:\n:::\n[\n%s\n]\n:::\n' % (index, Traverse.data.__str__())
            Traverse, index = Traverse.PreviousData, index + 1
        return display

    def RetrieveRecentNthQuery(self, n):
        """
        Return recently nth query, if exists in the list, else returns None
        """
        if n < 0:
            raise TypeError('Invalid nth query, n cannot be negative: found {}'.format(n))
        if n > self.Size:
            print('Recent nth query value n: {} exceeds history size: {}'.format(n, self.Size))
            return None
        else:
            Traverse, n = self.Tail, n - 1
            while n > 0:
                Traverse = Traverse.NextData
            return Traverse.Data
