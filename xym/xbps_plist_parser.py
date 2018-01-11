class XbpsPlistParser:
    plist = None

    def __init__(self, iterator):
        self.iterator = iterator
        self.plist = {}
        self.is_first = True
        self.parents = []
        self.tree = {}
        self.path = []
        self.parents_is_dict = []
        self.next_key = 'root'
        self.wants_data = False
        self.next_data = ""
        self.is_dict = True
        self.register = False
        self.curr = self.tree

    def push_tree(self, what, item=None):
        climb = False
        this_is_dict = False

        if what == 'dict':
            this_is_dict = True
            item = {}
            climb = True

        if what == 'array':
            this_is_dict = False
            item = []
            climb = True

        if self.register:
            if self.is_dict:
                self.curr[self.next_key] = item
            else:
                self.curr.append(item)

        if climb:
            self.parents.append(self.curr)
            if len(self.path) > 0 and self.path[-1] == 'root':
                self.register = True

            self.path.append(self.next_key)
            self.parents_is_dict.append(self.is_dict)
            self.curr = item
            self.is_dict = this_is_dict

        self.next_key = None

    def pull_tree(self):
        last_path = self.path.pop()

        if len(self.path) < 1 or self.path[-1] == 'root':
            self.register = False

        if len(self.path) > 0 and self.path[-1] == 'root':
            self.iterator(self.curr, key=last_path)

        self.is_dict = self.parents_is_dict.pop()
        self.curr = self.parents.pop()

    def start(self, tag, attr):
        self.wants_data = tag in ['string', 'integer', 'data', 'key']

        if tag in ['dict', 'array']:
            self.push_tree(tag)

        self.next_data = ""

    def end(self, tag):
        data = self.next_data
        self.next_data = ""

        if tag == 'plist':
            return

        if tag == 'key':
            self.next_key = data
            return

        if tag in ['dict', 'array']:
            self.pull_tree()
            return

        if tag in ['true', 'false']:
            self.push_tree('boolean', tag == 'true')
            return

        self.push_tree(tag, data)

    def data(self, data):
        if not self.wants_data:
            return

        self.next_data += data

    def close(self):
        return None