from flask import Flask, render_template, redirect, jsonify, request, url_for
import sklearn
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import numpy as np
from flask_mail import Mail,Message

app = Flask(__name__)
use_case=''
actor=''
line1={}
tech_sum=0
env_sum=0
UCP=0
UFP=0
CAF=0
FP=0
ufp_dic={}
com=''

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/document1.html")
def document1():
    return render_template("document1.html")  

@app.route("/document2.html")
def document2():
    return render_template("document2.html") 

@app.route("/functional.html")
def functional():
    return render_template("functional.html")         

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/Effort_cal.html")
def effort():
    return render_template("Effort_cal.html")   
    
@app.route("/Effort_cal.html" ,methods=['POST','GET'])
def effort1():
    global use_case,actor,line1,tech_sum,env_sum
    
    if request.method=="POST":
        use_case=request.form['use_case']
        actor=request.form['actor']
        use_case=use_case.split(',')
        actor=actor.split(',')


    return render_template("Effort_cal2.html", use_cases=use_case,actors=actor)

@app.route("/Effort_cal2.html" ,methods=['POST'])
def effort2():
    global use_case,actor,line1,tech_sum,env_sum
    line1={}
    if request.method=="POST":
        for i in actor:
            line_act=[]
            line=request.form.getlist(i)
            for j in line:
                j=j.split("#")
                line_act.append(j[1])
            line1[i]=line_act      
    return render_template("Effort_cal3.html")

@app.route("/Effort_cal3.html" ,methods=['POST'])
def effort3():
    global use_case,actor,line1,tech_sum,env_sum,UCP
    try:
        if request.method=="POST" and request.form['submit1']=="Submit1":
            tech=[]
            envr=[]
            tech_sum=0
            env_sum=0
            sol_dic={'1':1,'2':2,'3':3,'4':4,'5':5,'':2}
            if request.method=="POST":
                for i in range(1,14):
                    f=request.form[f"T{i}"]
                    tech.append(f)    
                for i in range(1,9):
                    f=request.form[f"E{i}"]
                    envr.append(f)
            te_s=[2,1,1,1,1,0.5,0.5,1,1,1,1,1,1]      
            en_s=[1.5,0.5,1,0.5,1,2,-1,-1]  
            for i in range(13):
                tech_sum+=sol_dic[tech[i]]*te_s[i]
            for i in range(8):
                env_sum+=sol_dic[envr[i]]*en_s[i] 
            
            tech_sum=0.6+ tech_sum/100
            env_sum=1.4 + env_sum*0.03
    except:        
        t_tech=''
        t_env=''
        if request.method=="POST":
            t_tech=request.form['techt']
            t_env=request.form['envt']  
        tech_dic={'1':0.74,'2':0.88,'3':1.02,'4':1.16,'5':1.3,'':0.88}
        env_dic={'1':1.535,'2':1.67,'3':1.805,'4':1.94,'5':2.075,"":1.67}
    
        tech_sum=tech_dic[t_tech]
        env_sum=env_dic[t_env]
         
    cv,model=pickle.load(open('model.pkl','rb'))
    uc_cv=cv.transform(use_case).toarray()
    use_case_com=model.predict(uc_cv)

    use_case_com_dic={}
    for i in range(len(use_case)):
        use_case_com_dic[use_case[i]]=use_case_com[i]

    actor_com_dic={}
    for i in range(len(actor)):
        line_list=line1[actor[i]]
        for j in range(len(line_list)):
            line_list[j]=use_case_com_dic[line_list[j]]
        simple=line_list.count(2)
        average=line_list.count(0)
        comp=line_list.count(1)
        r1=simple//3
        average+=r1
        r2=average//4
        comp+=r2
        if 0<comp:
            actor_com_dic[actor[i]]=1
        elif 0<average:
            actor_com_dic[actor[i]]=0
        else:
            actor_com_dic[actor[i]]=2  


    simple,avg,comp=0,0,0
    for i in use_case:
        if use_case_com_dic[i]==2:
            simple+=1
        elif use_case_com_dic[i]==0:
            avg+=1
        else:
            comp+=1
    UUCW=simple*5+avg*10+comp*15     

    simple,avg,comp=0,0,0
    for i in actor:
        if actor_com_dic[i]==2:
            simple+=1
        elif actor_com_dic[i]==0:
            avg+=1
        else:
            comp+=1 
    UAW=simple*1+avg*2+comp*3   

    TCF=tech_sum
    ECF=env_sum
    PF=20

    UCP=int((UUCW+UAW)*TCF*ECF)
    hours=int(UCP*PF)  

    com_dic={2:"Simple",1:"Complex",0:"Average"}
    for i in use_case_com_dic:
        a=use_case_com_dic[i]
        a=com_dic[a]
        use_case_com_dic[i]=a
    for i in actor_com_dic:
        a=actor_com_dic[i]
        a=com_dic[a]
        actor_com_dic[i]=a
          
    return render_template("result.html",use_case=use_case_com_dic,actor=actor_com_dic,
    UUCW=UUCW,UAW=UAW,TCF=TCF,ECF=ECF,PF=PF,UCP=UCP,hours=hours)

@app.route("/result1.html")
def result1():
    global UCP
    try:
        x=[14,16,18,20,22,24,26,28,30]
        y=[]
        for i in range(9):
            y.append(x[i]*UCP)
        x1=list(map(str,x))      
        plt.ylabel('Hours')
        plt.xlabel('Hours/UCP')
        plt.title('Analysis of Productivity Factor and Use Case Point')
        plt.xticks(range(len(x)),x1)
        bar1=plt.bar(np.arange(len(x)),y,0.35,align='center',alpha=0.8,color='b')
        for t in bar1:
            height=t.get_height()
            plt.text(t.get_x()+t.get_width()/2.0,height,f'{height:.0f}',ha='center',va='bottom')
        plt.legend()
        plt.tight_layout()    
        plt.savefig('static/plot.png')
    except:
        pass    
    return render_template("result1.html",url='static/plot.png') 

@app.route("/functional.html",methods=['POST'])
def fun1():
    global UFP,FP,CAF,ufp_dic,ufp_dic,com
    UFP=0
    ufp_dic={} 
    com=''  
    if request.method=="POST":
        com=request.form.get("Complexity")
        for i in range(5):
            x=request.form.get(f"U{i+1}")
            if x!="":
                ufp_dic[f"U{i+1}"]=request.form.get(f"U{i+1}",type=int)  
    ufp_weg1={"Simple":[3,4,3,7,5],"Average":[4,5,4,10,7],"Complex":[6,7,6,15,10]} 
    ufp_weg=ufp_weg1[com]
    for i in range(5):
        UFP+=ufp_dic[f"U{i+1}"]*ufp_weg[i]
    return render_template("functional2.html")
    
@app.route("/functional2.html",methods=['POST'])
def fun2():
    global CAF,FP,UFP,com
    CAF=0
    caf_dic={}
    opt={"0":0.65,"1":0.79,"2":0.93,"3":1.07,"4":1.21,"5":1.35}
    try:
        if request.method=="POST":
            st=request.form.get('Rate')
            CAF=opt[st]
    except:
        for i in range(14):
            caf_dic[f"F{i+1}"]=2  
        if request.method=="POST":
            for i in range(14):
                x=request.form.get(f"F{i+1}")
                if x!="":
                    caf_dic[f"F{i+1}"]=request.form.get(f"F{i+1}",type=int)   
        for i in range(14):
            CAF+=caf_dic[f"F{i+1}"]
        CAF= 0.65 + (0.01*CAF) 
    FP=int(UFP*CAF)
    effort_time_FP=int(FP*18)
    return render_template("funresult.html",UFP=UFP,CAF=CAF,ufp_dic=ufp_dic,FP=FP,effort_time_FP=effort_time_FP,com=com)

@app.route("/funresult2.html")
def fun3():
    global FP
    try:
        x=[10,12,14,16,18,20,22,24,26]
        y=[]
        for i in range(9):
            y.append(x[i]*FP)
        x1=list(map(str,x))      
        plt.ylabel('Hours')
        plt.xlabel('Hours/UCP')
        plt.title('Analysis of Productivity Factor and Functional Point')
        plt.xticks(range(len(x)),x1)
        bar1=plt.bar(np.arange(len(x)),y,0.35,align='center',alpha=0.8,color='b')
        for t in bar1:
            height=t.get_height()
            plt.text(t.get_x()+t.get_width()/2.0,height,f'{height:.0f}',ha='center',va='bottom')
        plt.legend()
        plt.tight_layout()    
        plt.savefig('static/plot2.png')
    except:
        pass    
    return render_template("funresult2.html",url='static/plot2.png') 

@app.route("/contact_us.html",methods=['POST','GET'])
def contact_us():
    ret=''
    my_email = "satishreso888@gmail.com"
    password = "Satish@01"
    recipient= ["satishreso888@gmail.com"]
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=8080
    app.config['MAIL_USERNAME']=my_email
    app.config['MAIL_PASSWORD']=password
    app.config['MAIL_USE_TLS']=False
    app.config['MAIL_USE_SSL']=True
    mail=Mail(app)
    if request.method=="POST":
        name = request.form['name']
        recipient2 = (request.form['email']).lower()
        message1 = request.form['message']
        msg=Message(name,sender=my_email,recipients=[recipient2,'satishmaurya010101@gmail.com'])
        msg.body=message1
        mail.send(msg)
        ret="Send the Message"          
    return render_template("contact_us.html",message=ret)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000,debug=True)    

