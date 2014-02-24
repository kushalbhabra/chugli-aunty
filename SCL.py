
#!/usr/bin/python

## Structure Chugli Language SCL

## Pre-Processing
# Returns a Query containing 5 Fields 
# method | Subject | number | exam | year 
def preprocessing(Subject):
        try:
                pQuery = Subject.strip().lower().split() # Strip trailing and starting case and lowercase
        except:
                print "Invalid Subject"
                return False
       
        Query = {}
        if len(pQuery) == 4:
                
                try:
                        
                        ## Case where subject and number is combined
                        import re 
                        Query['method'] = pQuery[0]
                        Query['subject'] = re.findall('(\d+|[a-zA-Z]+)',pQuery[1])[0]
                        Query['number'] = re.findall('(\d+|[a-zA-Z]+)',pQuery[1])[1]
                        Query['exam'] = pQuery[2]
                        Query['year'] = pQuery[3]
                except: 
                        print "Couldn't parse Subject properly | len(pQuery) == 4"
                        return False
        elif len(pQuery) == 5:
                try:
                        Query['method'] = pQuery[0]
                        Query['subject'] = pQuery[1]
                        Query['number'] = pQuery[2]
                        Query['exam'] = pQuery[3]
                        Query['year'] = pQuery[4]
                except:
                        print "Couldn't parse Subject properly | len(pQuery) == 5"
                        return False
        else:
                pass
        
        return Query


# Method 
def method(Query):
        method = Query['method'] 
        
        if method == "get":
                pass
        elif method == "put":
                pass
        else:
                print "Invalid method"
                return False
        return True

# Subject & Number | Exam | Year
def get_paper(Query):
        pass

sub = "  get ai688 midsem 08 " 
print preprocessing(sub)

# Easter Eggs

