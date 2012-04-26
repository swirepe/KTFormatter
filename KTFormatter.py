from argparse import ArgumentParser, RawDescriptionHelpFormatter
import textwrap
import os
import gzip
from collections import defaultdict
import time
import textwrap
import random
import json

class KTFormatter:
    def __init__(self):
        self.args = self.getArguments()
        self.parseArgs()
        
        # skill -> student -> [response]
        self.responses = defaultdict(lambda: defaultdict(list))
        
        
        
    def parseArgs(self):
        # input and header
        self.header = self.args.header
        self.input_file = self.args.input
        
        # output directory
        self.outputdir = self.args.output
        
        # columns
        self.skill_col = self.args.skill
        self.student_col = self.args.student
        self.response_col = self.args.response
        
        # compression
        self.compress = self.args.compress
        
        ## separators
        self.sep = ","
        if self.args.tabs_in:
            self.sep = "\t"
        elif self.args.spaces_in:
            self.sep = " "
        
        self.outsep = " "
        if self.args.tabs_out:
            self.outsep = "\t"
        elif self.args.spaces_out:
            self.outsep = " "
        
        # train/test splitting
        if self.args.train_percent == 0:
            self.traintest = False
        else:
            self.traintest = True
            
        self.train_percent = self.args.train_percent
        # if they input something like 70, we want that to be 0.70    
        if self.train_percent > 1:
            self.train_percent /= 100.0
            
        
        # skill/student splitting
        self.split_skill = self.args.split_by_skill
        self.split_student = self.args.split_by_student
        
        
        # using integer ids
        self.students_as_int = self.args.students_as_int
        self.student_id = IncrementMap(self.students_as_int)

        
        self.skills_as_int = self.args.skills_as_int
        self.skill_id = IncrementMap(self.skills_as_int)

            
        # kdd format (multiple skill, same column)
        self.kdd = self.args.kdd 

            

    def getArguments(self):
        description = "Split a file up by skill -> responses, and by train/test"
        
        epilog = textwrap.dedent('''\
            KT Formatter: Turn csvs into files suited for training knowledge tracing models.
            2012 Peter Swire - swirepe.com
            
            Example - breaking up the kdd cup data:
                dataFormatter 
                    --input bridge_to_algebra_2006_2007_train.txt
                    --output bridge
                    --student 1
                    --skill 17
                    --response 13 
                    --header
                    --tabs-in
                    --split-by-skill
                    --skills-as-int
                    --students-as-int
                    --kdd
                    --compress
                ''')
        
        
        parser = ArgumentParser(prog = "ktformatter",
            formatter_class = RawDescriptionHelpFormatter,
            description = description,
            epilog = epilog)
        
        parser.add_argument('-i', "--input", action="store", required=True, help="The CSV to chop up")
        parser.add_argument('-o', "--output", action="store", required=True, help="The directory to output files into")
        
        parser.add_argument('-s', "--skill", action="store", required=True, help="The column containing skill identifiers (starts at zero)", type=int)
        parser.add_argument('-r', "--response", action="store", required=True, help="The column containing responses (starts at zero).  Note, responses need to be either 0 or 1.", type=int)
        parser.add_argument('-p', "--student", action="store", required=True, help="The column containing person ids (starts at zero)", type=int)
        
        parser.add_argument('--header', action="store_true", help="The input csv contains a header that needs to be stripped")
        
        parser.add_argument('--train-percent', action="store", default=0, help="The percent of the total data to put into a training set.", type=float)
        
        parser.add_argument("--tabs-in", action="store_true", help="Input with separator as tabs (default is commas)")
        parser.add_argument("--spaces-in", action="store_true", help="Input with separator as spaces (default is commas)")
        
        parser.add_argument("--compress", action="store_true", default=True, help="Compress the output files with gzip")
        parser.add_argument("--split-by-skill", action="store_true", default=True, help="Output each skill separately")
        parser.add_argument("--split-by-student", action="store_true", default=False, help="Output each student separately (implies --split-by-skill)")
        parser.add_argument("--tabs-out", action="store_true", help="Output with separator as tabs (default is commas)")
        parser.add_argument("--spaces-out", action="store_true", help="Output with separator as spaces (default is commas)")
        
        
        parser.add_argument("--skills-as-int", action="store_true", default=False, help="Convert skills into integer ids")
        parser.add_argument("--students-as-int", action="store_true", default=False, help="Convert student ids into integer ids")
        
        parser.add_argument("--kdd", action="store_true", help="The KDD data has multiple skills in their skill column, separated by ~~.")
        
        return parser.parse_args()
    
    
    def makeDirectories(self):
        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)
            
        if self.traintest:
            try:
                os.mkdir( os.path.join( self.outputdir, "train"))
                os.mkdir( os.path.join( self.outputdir, "test"))
            except:
                pass
            
        # if we are splitting by student, we need a folder for each skill
        if self.split_student:
            skills = self.responses.keys()
            
            
            if self.traintest:
                paths = [os.path.join( self.outputdir, "train"),os.path.join( self.outputdir, "test")]
            else:
                paths = [self.outputdir]
                
            for skill in skills:
                for path in paths:
                    try:
                        os.mkdir( os.path.join( path, skill) )
                    except:
                        pass
            
            
    def parseFile(self):
        f = open(self.input_file)
        
        if self.header == True:
            _ = f.readline()
            
        for line in f.readlines():
            for (skill, student, response) in self.parseLine(line):
                self.responses[skill][student].append(response)
        
    
    
    def parseLine(self, line):
        line = line.split(self.sep)
        student = self.student_id(line[self.student_col])
        
        response = int(line[self.response_col])
        
        if self.kdd:
            skills = line[self.skill_col].split("~~")
            for skill in skills:
                skill = self.skill_id(skill)
                yield (skill, student, response)
        else:
            skill = self.skill_id(line[self.skill_col])
            yield (skill, student, response)
       
    
    
    def getFile(self, filename):
        if self.compress:
            return gzip.open(filename, 'wb')
        else:
            return open(filename, 'w')
    
    
    
    
    
    def getOutputNameForSkillFile(self, skill, opt=None):
        if self.compress:
                skill = str(skill) + ".gz"
        else:
            skill = str(skill) + ".csv"
            
        if opt == None:
            return os.path.join(self.outputdir, skill)
        else:
            return os.path.join(self.outputdir, opt, skill)
    
    
    
    def getOutputNameForStudentFile(self, skill, student, opt=None):
        if self.compress:
            student = str(student) + ".gz"
        else:
            student = str(student) + ".csv"
            
        if opt == None:
            return os.path.join(self.outputdir, skill, student)
        else:
            return os.path.join(self.outputdir, opt, skill, student)
    
    
    
    def _dumpBySkill(self):
        train = defaultdict(list)
        # glom together all of the students because don't care about spliting by student
        for skill, studentDict in self.responses.iteritems():
            for student in studentDict.keys():
                train[skill].append( self.responses[skill][student] )
    
        # split our monolithic thing into 2 by skill
        # each skill gets n% of the responses for that skill, roughly
        if self.traintest:
            train2 = defaultdict(list)
            test = defaultdict(list)
            
            for skill, responses in train.iteritems():
                for response in responses:
                    if random.random() < self.train_percent:
                        train2[skill].append(response)
                    else:
                        test[skill].append(response)
                 
            self.writeSkill(train2, "train")
            self.writeSkill(test, "test")
        else:
            self.writeSkill(train)
        
        
        
    def writeSkill(self, skilldict, opt=None):
        """Output responses, one skill per file
        opt means put in the train folder, the test folder, or the root folder"""
        for skill, responses in skilldict.iteritems():
            outblob = "\n".join([self.outsep.join(r) for r in responses])
            fname = getOutputNameForSkillFile(skill, opt)
            out = self.getFile(fname)
            out.write(outblob)
            out.close()
            
            
            
    def _dumpByStudent(self):
        def getName(skill, student, opt=None):
            if self.compress:
                student = str(student) + ".gz"
            else:
                student = str(student) + ".csv"
            if opt == None:
                return os.path.join(self.outputdir, skill, student)
            else:
                return os.path.join(self.outputdir, opt, skill, student)
        
        # student -> responses
        for skill, students in self.responses.iteritems():
            for student_id, responses in students.iteritems():
                
                if self.traintest:
                    toTrain = random.random() < self.train_percent
                    if toTrain:
                        opt = "train"
                    else:
                        opt = "test"
                    
                    name = getName(skill, student_id, opt)
                    
                    out = self.getFile(name)
                    out.write( self.outsep.join(responses))
                    out.close()
                else:
                    name = getName(skill, student_id)
                    out = self.getFile(name)
                    out.write( self.outsep.join(responses))
                    out.close()
                
                
            
            
    def _dumpAll(self):
        """Put everything into one big file, or two if we are train/test splitting"""
        def getName(filename):
           if self.compress:
                return os.path.join(self.outputdir, filename + ".gz")
           else:
               return os.path.join(self.outputdir, filename + ".csv")


        outlist = [self.outsep.join(r) for (skills, students) in self.responses.iteritems() for r in students.values()] 
        
        out.write(outblob)
        out.close()
        
        if self.traintest:
            random.shuffle(outlist)
            T = int(len(outlist) * self.train_percent)
            outtrain = self.getFile( getName("train") )
            outtrain.write( "\n".join( outlist[:T]  ) )
            outtrain.close()
            
            outtest = self.getFile( getName("test") )
            outtest.write( "\n".join(outlist[T:]) )
            outtest.close()
            
        else:
            out = self.getFile( getName("output") )
            out.write( "\n".join(outlist) )
            out.close()
                
            
        
        

    def dumpObjects(self):  
        if self.split_student:
            _dumpByStudent()
        elif self.split_skill:
            _dumpBySkill()
        else:
            _dumpAll()
            
        
    def dumpMaps(self):
        if self.students_as_int:
            out = open(os.path.join(self.outputdir, "studentMap.json"), "w")
            out.write(json.dumps(self.student_id.table))
            out.close()
            
        if self.skills_as_int:
            out = open(os.path.join(self.outputdir, "skillMap.json"), "w")
            out.write(json.dumps(self.skill_id.table))
            out.close()
            
        
    def run(self):
        print "[PRE] Started processing file", self.input_file
        start = time.time()
        self.parseFile()
        self.makeDirectories()
        self.dumpObjects()
        self.dumpMaps()
        print "[POST] Finished in ", int(time.time() - start), "seconds"
        
        

class IncrementMap:
    def __init__(self, liveMapping):
        self.liveMapping = liveMapping
        self.index = 1
        self.table = {}
        
        
    def __call__(self, lookup_id):
        if not self.liveMapping:
            return lookup_id
        
        try:
            return table[lookup_id]
        except:
            self.table[lookup_id] = self.index
            self.index += 1
            return (self.index - 1)
    

if __name__ == "__main__":
    ktf = KTFormatter() 
    ktf.run()
    
    
    
