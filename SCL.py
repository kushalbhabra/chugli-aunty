
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
        
# Sample Query: get ai 688 quiz 2009
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
			
			## Experimental
			Query['method'] = pQuery[0]
			Query['subject'] = pQuery[1]
			Query['number'] = pQuery[2]
        
	elif len(pQuery) == 5:
                try:
                        Query['method'] = pQuery[0]
                        Query['subject'] = pQuery[1]
                        Query['number'] = pQuery[2]
                        Query['exam'] = pQuery[3]
                        Query['year'] = pQuery[4]
                except:
                        print "Couldn't parse Subject properly | len(pQuery) == 5"
			Query['method'] = pQuery[0]
			Query['subject'] = pQuery[1]
			Query['number'] = pQuery[2]

        else:
		try:
			### will be evoked when random query is invoked
			#### Bad way to handle, but yeah, this works..####
			print "Query Length less than 4"
			## Experimental
			Query['method'] = pQuery[0]
			Query['subject'] = pQuery[1]
			Query['number'] = pQuery[2]
			
 		        return Query

		except:
			pass
	return Query
# Subject & Number | Exam | Year
def get_paper(Query):
        pass

if __name__ == "__main__":
	sub = "  get ai688 midsem 08 " 
	sub_asterisk = " get ai688 midsem *"
	exp = " get cl 455 * *"
	non_sense = "123 nasd"

	print "query", sub
	print preprocessing(sub)
	print'----------------------------'


	print "query-with-asterisk", sub_asterisk
	print preprocessing(sub_asterisk)
	print'----------------------------'
	
	print "non_sense: ", non_sense
	print preprocessing(non_sense)
	print'----------------------------'
	
	print "Exp Query:", exp
	print "Exp feature", preprocessing(exp)
# Easter Eggs

