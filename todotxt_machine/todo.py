#!/usr/bin/env python
# coding=utf-8
import re
import random
import urwid
from datetime import date

from todotxt_machine.terminal_operations import TerminalOperations

class Todo:
    """Single Todo item"""

    def __init__(self, item, index,
            colored="", priority="", contexts=[], projects=[],
            creation_date="", due_date="", completed_date=""):
        self.raw            = item.strip()
        self.raw_index      = index
        self.creation_date  = creation_date
        self.priority       = priority
        self.contexts       = contexts
        self.projects       = projects
        self.due_date       = due_date
        self.completed_date = completed_date
        self.colored        = self.highlight()
        # self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

    def update(self, item):
        self.raw            = item.strip()
        self.priority       = Todos.priority(item)
        self.contexts       = Todos.contexts(item)
        self.projects       = Todos.projects(item)
        self.creation_date  = Todos.creation_date(item)
        self.due_date       = Todos.due_date(item)
        self.completed_date = Todos.completed_date(item)
        self.colored        = self.highlight()
        # self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

    def __repr__(self):
        return repr({
            "raw":            self.raw,
            "colored":        self.colored,
            "raw_index":      self.raw_index,
            "priority":       self.priority,
            "contexts":       self.contexts,
            "projects":       self.projects,
            "creation_date":  self.creation_date,
            "due_date":       self.due_date,
            "completed_date": self.completed_date
        })

    def highlight(self, line="", show_due_date=True, show_contexts=True, show_projects=True):
        colored = self.raw if line == "" else line
        color_list = [colored]

        if colored[:2] == "x ":
            color_list = ('completed', color_list)
        else:
            words_to_be_highlighted = self.contexts + self.projects
            if self.due_date:
                words_to_be_highlighted.append("due:"+self.due_date)
            if self.creation_date:
                words_to_be_highlighted.append(self.creation_date)

            if words_to_be_highlighted:
                color_list = re.split("(" + "|".join([re.escape(w) for w in words_to_be_highlighted]) + ")", self.raw)
                for index, w in enumerate(color_list):
                   if w in self.contexts:
                       color_list[index] = ('context', w) if show_contexts else ''
                   elif w in self.projects:
                       color_list[index] = ('project', w) if show_projects else ''
                   elif w == "due:"+self.due_date:
                       color_list[index] = ('due_date', w) if show_due_date else ''
                   elif w == self.creation_date:
                       color_list[index] = ('creation_date', w)

            if self.priority and self.priority in "ABCDEF":
                color_list = ("priority_{0}".format(self.priority.lower()), color_list)
            else:
                color_list = ("plain", color_list)

        return color_list

    def highlight_search_matches(self, line=""):
        colored = self.raw if line == "" else line
        color_list = [colored]
        if self.search_matches:
            color_list = re.split("(" + "|".join([re.escape(match) for match in self.search_matches]) + ")", self.raw)
            for index, w in enumerate(color_list):
                if w in self.search_matches:
                    color_list[index] = ('search_match', w)
        return color_list

    def is_complete(self):
        if self.raw[0:2] == "x ":
            return True
        elif self.completed_date == "":
            return False
        else:
            return True

    def complete(self):
        today = date.today()
        self.raw = "x {0} ".format(today) + self.raw
        self.completed_date = "{0}".format(today)
        self.update(self.raw)

    def incomplete(self):
        self.raw = re.sub(Todos._completed_regex, "", self.raw)
        self.completed_date = ""
        self.update(self.raw)

    def add_creation_date(self):
        if self.creation_date == "":
            p = "({0}) ".format(self.priority) if self.priority != "" else ""
            self.update("{0}{1} {2}".format(p, date.today(), self.raw.replace(p, "")))


class Todos:
    """Todo items"""
    _context_regex       = re.compile(r'(?:^|\s+)(@\S+)')
    _project_regex       = re.compile(r'(?:^|\s+)(\+\S+)')
    _creation_date_regex = re.compile(r'^'
                                      r'(?:x \d\d\d\d-\d\d-\d\d )?'
                                      r'(?:\(\w\) )?'
                                      r'(\d\d\d\d-\d\d-\d\d)\s*')
    _due_date_regex      = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    _priority_regex      = re.compile(r'\(([A-Z])\) ')
    _completed_regex     = re.compile(r'^x (\d\d\d\d-\d\d-\d\d) ')

    def __init__(self, todo_items, file_path, archive_path):
        self.file_path = file_path
        self.archive_path = archive_path
        self.update(todo_items)

    def reload_from_file(self):
        with open(self.file_path, "r") as todotxt_file:
            self.update(todotxt_file.readlines())

    def save(self):
        with open(self.file_path, "w") as todotxt_file:
            for t in self.todo_items:
                todotxt_file.write(t.raw + '\n')

    def archive_done(self):
        if self.archive_path is not None:
            with open(self.archive_path, "a") as donetxt_file:
                done = self.done_items()
                for t in done:
                    donetxt_file.write(t.raw + '\n')
                    self.todo_items.remove(t)

            self.save()
            return True

        return False

    def update(self, todo_items):
        self.parse_raw_entries(todo_items)

    def append(self, item, add_creation_date=True):
        self.insert(len(self.todo_items), item, add_creation_date)
        return len(self.todo_items)-1

    def insert(self, index, item, add_creation_date=True):
        self.todo_items.insert(index, self.create_todo(item, index) )
        self.update_raw_indices()
        newtodo = self.todo_items[index]
        if add_creation_date and newtodo.creation_date == "":
            newtodo.add_creation_date()
        return index

    def delete(self, index):
        del self.todo_items[index]
        self.update_raw_indices()

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def next(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def __len__(self):
        return len(self.todo_items)

    def pending_items(self):
        return [t for t in self.todo_items if not t.is_complete()]

    def done_items(self):
        return [t for t in self.todo_items if t.is_complete()]

    def pending_items_count(self):
        return len(self.pending_items())

    def done_items_count(self):
        return len(self.done_items())

    def __getitem__(self, index):
        return self.todo_items[index]

    def __repr__(self):
        return repr( [i for i in self.todo_items] )

    def create_todo(self, todo, index):
        return Todo(todo, index,
            contexts       = Todos.contexts(todo),
            projects       = Todos.projects(todo),
            priority       = Todos.priority(todo),
            creation_date  = Todos.creation_date(todo),
            due_date       = Todos.due_date(todo),
            completed_date = Todos.completed_date(todo))

    def parse_raw_entries(self, raw_items):
        self.todo_items = [
            self.create_todo(todo, index)
            for index, todo in enumerate(raw_items) if todo.strip() != ""]

    def update_raw_indices(self):
        for index, todo in enumerate(self.todo_items):
            todo.raw_index = index

    @staticmethod
    def contexts(item):
        return sorted( Todos._context_regex.findall(item) )

    @staticmethod
    def projects(item):
        return sorted( Todos._project_regex.findall(item) )

    @staticmethod
    def creation_date(item):
        match = Todos._creation_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def due_date(item):
        match = Todos._due_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def priority(item):
        match = Todos._priority_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def completed_date(item):
        match = Todos._completed_regex.match(item)
        return match.group(1) if match else ""

    def all_contexts(self):
        # Nested Loop
        # all_contexts = []
        # for item in self.raw_items:
        #   for found_context in self.contexts(item):
        #     if found_context not in all_contexts:
        #       all_contexts.append(found_context)
        # return all_contexts

        # List comprehension
        # return sorted(set( [found_context for item in self.raw_items for found_context in self.contexts(item)] ))

        # Join all items and use one regex.findall
        # return sorted(set( Todos._context_regex.findall(" ".join(self.raw_items))))

        return sorted(set( [context for todo in self.todo_items for context in todo.contexts] ))

    def all_projects(self):
        # List comprehension
        # return sorted(set( [project for item in self.raw_items for project in self.projects(item)] ))

        # Join all items and use one regex.findall
        # return sorted(set( Todos._project_regex.findall(" ".join(self.raw_items))))

        return sorted(set([project for todo in self.todo_items for project in todo.projects] ))

    def sorted(self, reversed_sort=False):
        self.todo_items.sort( key=lambda todo: todo.raw, reverse=reversed_sort )

    def sorted_reverse(self):
        self.sorted(reversed_sort=True)

    def sorted_raw(self):
        self.todo_items.sort( key=lambda todo: todo.raw_index )

    def swap(self, first, second):
        """
        Swap items indexed by *first* and *second*.

        Out-of-bounds situations are handled by wrapping.
        """
        if second < first:
            second, first = first, second

        n_items = len(self.todo_items)

        if first < 0:
            first += n_items

        if second >= n_items:
            second = n_items - second

        self.todo_items[first], self.todo_items[second] = self.todo_items[second], self.todo_items[first]

    def filter_context(self, context):
        return [item for item in self.todo_items if context in item.contexts]

    def filter_project(self, project):
        return [item for item in self.todo_items if project in item.projects]

    def filter_context_and_project(self, context, project):
        return [item for item in self.todo_items if project in item.projects and context in item.contexts]

    def filter_contexts_and_projects(self, contexts, projects):
        return [item for item in self.todo_items if set(projects) & set(item.projects) or set(contexts) & set(item.contexts)]

    def search(self, search_string):
        search_string = re.escape(search_string)
        # print(search_string)
        ss = []
        substrings = search_string.split("\\")
        for index, substring in enumerate(substrings):
            s = ".*?".join(substring)
            # s.replace(" .*?", " ")
            if 0 < index < len(substrings)-1:
                s += ".*?"
            ss.append(s)
        # print(repr(ss))
        search_string_regex  = '^.*('
        search_string_regex += "\\".join(ss)
        search_string_regex += ').*'
        # print(search_string_regex)

        r = re.compile(search_string_regex, re.IGNORECASE)
        results = []
        for t in self.todo_items:
            match = r.search(t.raw)
            if match:
                t.search_matches = match.groups()
                results.append(t)
        return results

    quotes = [
        "What you really believe about the source of great performance thus becomes the foundation of all you will ever achieve -- Geoff Colvin, Talent is Overrated: What Really Separates World-Class Performers from Everybody Else",
        "Do not let your good ideas to spend your brain energy, do it with all the effort because the shadow of the success can become a reality only with hard work.  -- Isra",
        "I'm exhausted. I spent all morning putting in a comma and all afternoon taking it out -- Oscar Wilde",
        "Prescribing hard work for the soft, or easy work for the hardy, is generally nonsense. What is always needed in any aim is right effort, right time, right people, right materials.  -- Idries Shah, Reflections",
        "Easy and difficult things are juat small parts of life, the rest are what have to be done.  -- Alief Moulana",
        "Hard work is much more important than talent -- Carlo Rotella",
        "Wrote my way out of the hood...thought my way out of poverty! Don't tell me that knowledge isn't power. Education changes everything.  -- Brandi L. Bates",
        "Everything yields to diligence -- Thomas Jefferson",
        "Embrace the pain to inherit the gain.  -- Habeeb Akande",
        "If you don't burn out at the end of each day, you're a bum.  -- George Lois",
        "If you work hard and study hard. And you fuck up. That's okay. If you fuck up and you fuck up, then you're a fuckup -- Justin Halpern, Sh*t My Dad Says",
        "Patience can be bitter but her fruit is always sweet.  -- Habeeb Akande",
        "Greatness is sifted through the grind, therefore don't despise the hard work now for surely it will be worth it in the end.  -- Sanjo Jendayi",
        "You know how when you step on court your coach is like 'go go go!'? And all throughout you just keep telling yourself to hit harder and harder and keep at it? You know how much you treasure those five-minute timeouts? You know how good you feel at the end of a session? You know how you're glad you're tired? No pills, no shots, just plain energy. I want to work like that. Whether I have to write ten thousand words or send five hundred emails, brainstorm for hours at a time, I want to have that energy. To keep fighting. To know it's all worth it.  -- Thisuri Wanniarachchi",
        "Many say'What goes up must come down.' I believe this was spoken by a pessimist. I believe it is vitally important to remember that'What goes up...must have started some place.d -- Jayce O'Neal",
        "When you are pursuing your dreams, they will call you CRAZY because they are LAZY. They never know you are a HERO who just jumped away from step ZERO.  Stay away from negative people; they will only pollute you.  -- Israelmore Ayivor",
        "learning texts is worth doing not because it's easy but because it's hard.  -- Joshua Foer, Moonwalking with Einstein: The Art and Science of Remembering Everything",
        "Hard-earned good money is hard to waste; but can still have some good moments.  -- POB Bismark",
        "Talent is what God gives us, Skill is what we give back to Him -- Eliel Pierre",
        "Work as if there's no one to help you, and learn as if everybody is with you.  -- saransh garg",
        "To achieve what 1% of the worlds population has (Financial Freedom), you must be willing to do what only 1% dare to do..hard work and perseverance of highest order.  -- Manoj Arora, From the Rat Race to Financial Freedom",
        "Believe that your hard work, dedication and persistence will pay off; improve through continual learning and believe in your future.  -- Lorii Myers, No Excuses, The Fit Mind-Fit Body Strategy Book",
        "There is an open circle. -- John Passaro",
        "Love what you do, do it with passion, work hard, and never give up. Money and happiness will come to you.  -- Joseph C. Kunz Jr. ",
        "Only cooked time tastes well -- Zeeshan Ahmed",
        "Sometimes the greatest thing to come out of all your hard work isn't what you GET for it, but what you BECOME for it.  -- Steve Maraboli, Unapologetically You: Reflections on Life and the Human Experience",
        "Be Patient to become a Patent -- Zeeshan Ahmed",
        "I dropped out of school and congratulated myself for my diligence. Few realize how hard one has to work to resist the pressures of conventional success.  -- Bauvard, The Prince Of Plungers",
        "I need to dream.  -- John Passaro, 6 Minutes Wrestling With Life",
        "I'm lazy! I hate work! Hate hard work in all its forms! Clever shortcuts, that's all I'm about!  -- Eliezer Yudkowsky, Harry Potter and the Methods of Rationality",
        "We must strive for literacy and education that teach us to never quit questioning and probing at the assumptions of the day.  -- Bryant McGill, Voice of Reason",
        "I have learned that real angels don't have gossamer white robes and Cherubic skin, they have calloused hands and smell of the days' sweat.  -- Richard Paul Evans, Lost December",
        "Success necessitates sacrifice.  -- Habeeb Akande",
        "You always need to work hard.  You always need to be willing to work hard.  Not everything will be hard, but you should, at the very least, be willing to work hard.  -- Tom Giaquinto, Be A Good Human",
        "Do the things you like to be happier, stronger & more successful. Only so is hard work replaced by dedication.  -- Rossana Condoleo",
        "There comes a point when you have to realize that the sum of all your blood, sweat, and tears will ultimately amount to zero.  -- Max Brooks, World War Z: An Oral History of the Zombie War",
        "There is something beautiful in you seeking freedom.  -- Bryant McGill, Voice of Reason",
        "Be like a duck, paddling and working very hard inside the water, but what everyone sees is a smiling and calm face.  -- Manoj Arora, From the Rat Race to Financial Freedom",
        "If you are not working towards something, your life will end with nothing.  -- Habeeb Akande",
        "Respect your dream.  -- Jill Williamson, Go Teen Writers: How to Turn Your First Draft into a Published Book",
        "Hard work beats talent when talent fails to work hard.  -- Kevin Durant",
        "Im not a very good sleeper. But you know what? I'm willing to put in a few extra hours every day to get better. That's just the kind of hard worker I am.  -- Jarod Kintz, Whenever You're Gone, I'm Here For You",
        "Persistence and passion will make you invincible.  -- Christian Baloga",
        "When God calls you to build 100 castles on earth and you built 98, take the 99th as if it's the begining of your work and work hard to finish the race with all excellence. Go the extra mile!  -- Israelmore Ayivor",
        # "It's a complex song, and it's fascinating to watch the creative process as they went back and forth and finally created it over a few months. Lennon was always my favorite Beatle. [ He laughs as Lennon stops during the first take and makes the band go back and revise a chord.] Did you hear that little detour they took? It didn't work, so they went back and started from where they were. It's so raw in this version. It actually makes the sound like mere mortals. You could actually imagine other people doing this, up to this version. Maybe not writing and conceiving it, but certainly playing it. Yet they just didn't stop. They were such perfectionists they kept it going This made a big impression on me when I was in my thirties. You could just tell how much they worked at this.  -- Walter Isaacson, Steve Jobs",
        "All success comes down to this . . . action -- Rob Liano",
        "It is very rare for a child of God to find gold and crude oil on the floor to fetch. He/she must dig and dig deeply well!!!  -- Israelmore Ayivor",
        "When the grass is greener at other people's feet, it is not because the grass chose to take up that complexion. But it is because, they have deliberately irrigated it on regular accounts.  -- Israelmore Ayivor",
        "Some people dream of SUCCESS while other wake up and work hard at it.  -- Barbara Rubel",
        "If you want a fried fish to fly and enter your mouth, you must keep waiting till the unending time ends. Dead fish doesn't fly. If you want to eat it, your own hands must carry it.  -- Israelmore Ayivor",
        "Loosers want it but only through the easy way. If action taking were like reading a story book, loosers would only love to open the picture pages -- Israelmore Ayivor",
        "Virginity comes standard. A good head is earned.  -- Mokokoma Mokhonoana",
        "I've never felt that the American Dream was owed to me. I never felt that I was entitled to this Dream. This is why I laid the cobblestone before me for this Dream to be achieved.  -- John-Talmage Mathis, I Deal to Plunder - A ride through the boom town",
        "As I tell my children, 'If you are going to do something, do your best while you're doing it.  -- Michelle    Moore, Selling Simplified",
        "The more civilized people are, the more honorable working hard is to them. As a result, the more civilized we get, the less we live.  -- Mokokoma Mokhonoana",
        "Children take joy in their work and sometimes as adults we forget that's something we should continue doing.  -- Ashley Ormon, God in Your Morning",
        "If you want your dreams to work out for you, you must work with them. Pay the price and have the package of your accomplishments in full versions.  -- Israelmore Ayivor",
        "Nonetheless, the fact remains; he had hope in a better world he could not yet see that overwhelmed the cries of'you can't' or'you won't' or'why bother.'   More than anything else, mastering that faith, on cue, is what separated him from his peers, and distinguishes him from so many people in these literal, sophisticated times.   It has made all the difference.  -- Ron Suskind, A Hope in the Unseen: An American Odyssey from the Inner City to the Ivy League",
        "Ideas do not work..  -- Manoj Arora, From the Rat Race to Financial Freedom",
        "Stop and say something good about yourself! Believe what you have just said! Pray for what you have just believed! Have faith for what you just prayed for! Work out that faith! ...and surely goodness and mercy shall follow you!  -- Israelmore Ayivor",
        "It may be that you will be happiest in the rat race; perhaps, like me, you are basically a rat.  -- Richard Koch, The 80/20 Principle: The Secret to Achieving More with Less",
        "The world is moved along, not only by the mighty shoves of its heroes, but also by the aggregate of tiny pushes of each honest worker.  -- Helen Keller",
        "Your dreams are like the cement. If you water it with actions, it becomes a hard concrete mass. But if you leave it exposed and unwatered, the air will easily blow it away!  -- Israelmore Ayivor",
        "You may have the greatest vision, plans or goals as you may term it. You can call it Vison 2020, Vision 2045 or whatever. But remember, not work is done unless a distance is covered!  -- Israelmore Ayivor",
        "As I see it, if you work more hours than somebody else, during those hours you learn more about your craft. That can make you more efficient, more able, even happier. Hard work is like compounded interest in the bank. The rewards build faster.  -- Randy Pausch, The Last Lecture",
        "For a great tomorrow, plan today. Because every tomorrow becomes today, and every today becomes tomorrow. -- Richmond Akhigbe",
        "This should have been a red flag, I realize in retrospect. Working really hard on anything is, by definition, not cool.  -- Leila Sales, This Song Will Save Your Life",
        "I want the peace in knowing that is wasn't for lack of hustling that I missed a target for my dream. I want to know that the one thing in my control was under control.  -- Jon Acuff, Quitter: Closing the Gap Between Your Day Job and Your Dream Job",
        "Though you can love what you do not master, you cannot master what you do not love.  -- Mokokoma Mokhonoana",
        "Today's marriages become toxic, with resentments, after only a few years. It's one thing to say, 'I forgive,' but most lack the enterprise to do the necessary work that follows. It was the day after that proved who had the wisdom of God and who didn't.  -- Michael Ben Zehabe, Song of Songs the book for daughters",
        "I believe in success.  -- Himmilicious",
        "The pretty ones are usually unhappy. They expect everyone to be enamored of their beauty. How can a person be content when their happiness lies in someone else's hands, ready to be crushed at any moment? Ordinary-looking people are far superior, because they are forced to actually work hard to achieve their goals, instead of expecting people to fall all over themselves to help them.  -- J. Cornell Michel, Jordan's Brains: A Zombie Evolution",
        "I can only strive for what is important -- Rosie Thomas, Iris And Ruby",
        "To be a great achiever, you must first discover your main purpose of existing through feasible communication mode with your maker, the source of your destiny. This brings you a conviction to work with.  -- Israelmore Ayivor, Michelangelo | Beethoven | Shakespeare: 15 Things Common to Great Achievers",
        "A block won't move without the effort.  -- Isabella Poretsis",
        "People have struggled for the benefits of others, you can struggle at least for your own benefit.  -- Amit Kalantri",
        "Man was designed in a way in which he must eat in order to give him a solid reason to go to work everyday. This helps to keep him out of trouble. God is wise.  -- Criss Jami",
        "Submitting seemed to me a lot like giving up. If God gave us the strength to bail- the gumption to try and save ourselves- isn't that what he wanted us to do?  -- Jeannette Walls, Half Broke Horses",
        "Too many irons, not enough fire.  -- S. Kelley Harrell",
        "Ah? A small aversion to menial labor?' The doctor cocked an eyebrow.'Understandable, but misplaced. One should treasure those hum-drum tasks that keep the body occupied but leave the mind and heart unfettered.  -- Tad Williams, The Dragonbone Chair",
        "I'm really very self-confident when it comes to my work. When I take on a project, I believe in it 100%. I really put my soul into it. I'd die for it. That's how I am -- Michael  Jackson",
        "Create with the heart; build with the mind.  -- Criss Jami",
        "Praying without working is faith inaction.  -- Saji Ijiyemi",
        "Such is life. It is no cleaner than a kitchen; it reeks like a kitchen; and if you mean to cook your dinner, you must expect to soil your hands; the real art is in getting them clean again, and therein lies the whole morality of our epoch.  -- Honore de Balzac, Pere Goriot",
        "It's a question of attitude. If you really work at something you can do it up to a point. If you really work at being happy you can do it up to a point. But anything more than that you can't. Anything more than that is luck.  -- Haruki Murakami, Dance Dance Dance",
        "With intellectual labor your hard work is forever, while with manual labor your hard work is temporary and soon forgotten.  -- Jarod Kintz, At even one penny, this book would be overpriced. In fact, free is too expensive, because you'd still waste time by reading it. ",
        "I feel as though whenever I create something, my Mr. Hyde wakes up in the middle of the night and starts thrashing it. I sometimes love it the next morning, but other times it is an abomination.  -- Criss Jami",
        "Does the work get easier once you know what you are doing?' -- Christopher Moore, Lamb: The Gospel According to Biff, Christ's Childhood Pal",
        "All good work requires self-revelation.  -- Sidney Lumet, Making Movies",
        "I've always resented the smug statements of politicians, media commentators, corporate executives who talked of how, in America, if you worked hard you would become rich.  The meaning of that was if you were poor it was because you hadn't worked hard enough.  I knew this was a lite, about my father and millions of others, men and women who worked harder than anyone, harder than financiers and politicians, harder than anybody if you accept that when you work at an unpleasant job that makes it very hard work indeed.  -- Howard Zinn, You Can't Be Neutral on a Moving Train: A Personal History of Our Times",
        "Hard work without talent is a shame, but talent without hard work is a tragedy -- Robert Half",
        "Sometimes it takes a lowly, title-less man to humble the world. Kings, rulers, CEOs, judges, doctors, pastors, they are already expected to be greater and wiser.  -- Criss Jami, Venus in Arms",
        "If your dream is a big dream, and if you want your life to work on the high level that you say you do, there's no way around doing the work it takes to get you there.  -- Joyce Chapman",
        "I do not care about happiness simply because I believe that joy is something worth fighting for.  -- Criss Jami",
        "The writer's curse is that even in solitude, no matter its duration, he never grows lonely or bored.  -- Criss Jami",
        "If wealth was the inevitable result of hard work and enterprise, every woman in Africa would be a millionaire.  -- George Monbiot",
        "I'm really very self-confident when it comes to my work. When I take on a project, I believe in it 100%. I really put my soul into it. I'd die for it. That's how I am.  -- Michael  Jackson",
        "In the land where excellence is commended, not envied, where weakness is aided, not mocked, there is no question as to how its inhabitants are all superhuman.  -- Criss Jami, Venus in Arms",
        "No one ever drowned in sweat.  -- United States Marine Corps",
        "What is hard work? It takes strength, energy, and stress to truly care about others enough to place oneself last, but it is easy to wrap oneself up and selfishly scramble on the heads of others.  -- Criss Jami",
        "I don't have a blue-collar job. It's more of a green collar, because of all the yellow sweat stains mixing in.   -- Jarod Kintz, This Book Has No Title",
        "As Aristotle said, 'Excellence is a habit.' I would say furthermore that excellence is made constant through the feeling that comes right after one has completed a work which he himself finds undeniably awe-inspiring. He only wants to relax until he's ready to renew such a feeling all over again because to him, all else has become absolutely trivial.  -- Criss Jami",
        "Inspiration is the windfall from hard work and focus. Muses are too unreliable to keep on the payroll.  -- Helen Hanson",
        "The idea that the harder you work, the better you're going to be is just garbage. The greatest improvement is made by the man or woman who works most intelligently.  -- Bill Bowerman",
        "You were hired because you met expectations, you will be promoted if you can exceed them.  -- Saji Ijiyemi",
        "People.. were poor not because they were stupid or lazy. They worked all day long, doing complex physical tasks. They were poor because the financial institution in the country did not help them widen their economic base.  -- Muhammad Yunus, Banker to the Poor: Micro-Lending and the Battle Against World Poverty",
        "She was tough in the best sense of the word.  She'd taken blows, the disappointments, and had worked her way through them.  Some people, he knew, would have buckled under, found a clutch, or given up.  But she had carved a place for herself and made it work.  -- Nora Roberts",
        "A clay pot sitting in the sun will always be a clay pot.  It has to go through the white heat of the furnace to become porcelain.  -- Mildred W. Struven",
        "Barking hard work, being boy.  -- Scott Westerfeld, Leviathan",
        "Do I attribute my success to hard work, or sunscreen? If you want the truth, maybe you should ask my new albino secretary.   -- Jarod Kintz, At even one penny, this book would be overpriced. In fact, free is too expensive, because you'd still waste time by reading it. ",
        "Sometimes there's not a better way. Sometimes there's only the hard way.  -- Mary E. Pearson, The Fox Inheritance",
        "The harder you fall, the heavier your heart; the heavier your heart, the stronger you climb; the stronger you climb, the higher your pedestal.  -- Criss Jami",
        "Every job from the heart is, ultimately, of equal value. The nurse injects the syringe; the writer slides the pen; the farmer plows the dirt; the comedian draws the laughter. Monetary income is the perfect deceiver of a man's true worth.  -- Criss Jami",
        "It is a pity that doing one's best does not always answer.  -- Charlotte Brontë, Jane Eyre",
        "I don't like to celebrate my birthday, because I don't like taking credit for others' work—in this case, my mom and dad. Or possibly my mom and the mailman.  -- Jarod Kintz, This Book Has No Title",
        "The dictionary is the only place that success comes  before work. work is the key to success, and hard work can help you accomplish anything.  -- Vince Lombardi",
        "Many who are self-taught far excel the doctors, masters, and bachelors of the most renowned universities.  -- Ludwig von Mises",
        "...talent means nothing, while experience, acquired in humility and with hard work, means everything.  -- Patrick Süskind, Perfume: The Story of a Murderer",
        "No one understands and appreciates the American Dream of hard work leading to material rewards better than a non-American.  -- Anthony Bourdain, Kitchen Confidential: Adventures in the Culinary Underbelly",
        "The difference between ordinary and extraordinary is that little extra.  -- Jimmy Johnson",
        "The year you were born marks only your entry into the world. Other years where you prove your worth, they are the ones worth celebrating.   -- Jarod Kintz, This Book Title is Invisible",
        "Don't wish it were easier. Wish you were better.  -- Jim Rohn",
        "There are no shortcuts to any place worth going.  -- Beverly Sills",
        "Determine never to be idle.  No person will have occasion to complain of the want of time, who never loses any.  It is wonderful how much may be done, if we are always doing.  -- Thomas Jefferson",
        "The three great essentials to achieve anything worthwhile are, first, hard work; second, stick-to-itiveness; third, common sense.  -- Thomas A. Edison",
        "I'm a greater believer in luck, and I find the harder I work the more I have of it -- Thomas Jefferson",
        "If you try and lose then it isn't your fault. But if you don't try and we lose, then it's all your fault.  -- Orson Scott Card, Ender's Game",
        "Make a pact with yourself today to not be defined by your past. Sometimes the greatest thing to come out of all your hard work isn't what you get for it, but what you become for it. Shake things up today! Be You...Be Free...Share.  -- Steve Maraboli, Life, the Truth, and Being Free",
        "If I told you I've worked hard to get where I'm at, I'd be lying, because I have no idea where I am right now.  -- Jarod Kintz, This Book is Not for Sale",
        "It's hard to beat a person who never gives up.  -- Babe Ruth",
        "The best way to not feel hopeless is to get up and do something. Don't wait for good things to happen to you. If you go out and make some good things happen, you will fill the world with hope, you will fill yourself with hope. -- Barack Obama",
        "The only man who never makes mistakes is the man who never does anything. --  Theodore Roosevelt",
        "What would life be if we had no courage to attempt anything? -- Vincent van Gogh",
        "Far better it is to dare mighty things, to win glorious triumphs, even though checkered by failure, than to take rank with those poor spirits who neither enjoy much nor suffer much, because they live in the gray twilight that knows neither victory nor defeat. -- Theodore Roosevelt, Strenuous Life",
        "...wanting change is step one, but step two is taking it. -- Isaac Marion, Warm Bodies",
        "Make voyages. Attempt them. There's nothing else. -- Tennessee Williams, Camino Real",
        "Do more than belong: participate. Do more than care: help. Do more than believe: practice. Do more than be fair: be kind. Do more than forgive: forget. Do more than dream: work. -- William Arthur Ward",
        "To live a creative life, we must lose our fear of being wrong. -- Joseph Chilton Pearce",
        "I love to sail forbidden seas, and land on barbarous coasts. -- Herman Melville",
        "Do anything, save to lie down and die! -- Nathaniel Hawthorne, The Scarlet Letter",
        "Whatever the mind of man can conceive and believe, it can achieve -- W. Clement Stone",
        "He who waits to do a great deal of good at once will never do anything. -- Samuel Johnson",
        "There's doubt in trying.  Just do it or stop thinking. -- Toba Beta, Master of Stupidity",
        "You'll never know the the outcome unless you just go out there and just do it. -- Jonathan Anthony Burkett, Neglected But Undefeated: The Life Of A Boy Who Never Knew A Mother's Love",
        "The only dreams that matter are the ones you have when you're awake. -- John O'Callaghan",
        "A person can choose to stand against adversity, but most people will run from it before they come to terms with who they truly are, a wise person watches through adversity and follows the signs when it is their turn to stand. -- Faith Brashear",
        "People tell you that you cannot, because they do not. -- Tim Fargo",
    ]

    @staticmethod
    def quote():
        return Todos.quotes[ random.randrange(len(Todos.quotes)) ]
