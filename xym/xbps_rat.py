import string

from ratking import Rat, RatVersion, RatSelector
from ratking.version_selector.clauses import AnyClause


class XbpsRat(Rat):
    raw_version = None
    raw_dict = None

    cache_version = None
    cache_needs = None
    cache_provides = None

    def __init__(self, name, raw_version, raw_dict, repo=None):
        self.name = name
        self.raw_version = raw_version
        self.raw_dict = raw_dict
        self.repo = repo

    @property
    def version(self):
        if self.cache_version is None:
            self.cache_version = RatVersion.from_str(self.raw_version)

        return self.cache_version

    @property
    def provides(self):
        return self.raw_dict.get('shlib-provides', [])

    @property
    def needs(self):
        if self.cache_needs is None:
            needs = []
            for shlib in self.raw_dict.get('shlib-requires', []):
                needs.append(RatSelector(shlib, AnyClause()))

            for depend in self.raw_dict.get('run_depends', []):
                if '>' in depend:
                    pos = depend.find('>')
                    name = depend[:pos]
                    sel = depend[pos:]
                    if sel == '>=' or '>':
                        needs.append(RatSelector(name, AnyClause()))
                        continue

                    needs.append(RatSelector.from_str_pair(name, sel))
                    continue

                if '<' in depend:
                    pos = depend.find('<')
                    name = depend[:pos]
                    sel = depend[pos:]
                    if sel == '<=' or '<':
                        needs.append(RatSelector(name, AnyClause()))
                        continue

                    needs.append(RatSelector.from_str_pair(name, sel))
                    continue

                parts = depend.rsplit('-', maxsplit=1)

                if len(parts) == 1 or not parts[1][0] in string.digits:
                    needs.append(RatSelector(depend, AnyClause()))

                needs.append(RatSelector.from_str_pair(parts[0], parts[1]))

            self.cache_needs = needs

        return self.cache_needs

