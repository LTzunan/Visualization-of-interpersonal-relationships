import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Graph
import webbrowser

    
Dir_hobby=['运动','学习','娱乐','游戏']
    
def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a 
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim

def main():
    Survey = pd.read_csv('./模拟数据.csv', encoding = "gbk")
    Survey = np.array(Survey)

    #所用参与问卷的学生
    Num = Survey[:,0]
    Students = Survey[:,1]
    Dictionary=dict(zip(Students,Num))

    #用户对于兴趣爱好的评分矩阵
    Hobby = np.zeros([Survey.shape[1]-4,Survey.shape[0]],dtype='O')

    for i in range(4,Survey.shape[1]):
        Hobby[i-4] = Survey[:,i]

    #兴趣偏好向量
    HobPer = Hobby.transpose()

    #社团
    C = [[] for i in range(len(Students))]
  
    #聚合
    C[0].append(Students[0])
    for i in range(1,len(Students)):
        for j in range(len(C)):
        
            if(len(C[j]) == 0):
                C[j].append(Students[i])
                break
        
            CS = 0                        #社团 cos(u,v)凝聚度 cs（community cohesion）
        
            for k in range(len(C[j])):
                CS+=cos_sim(HobPer[i],HobPer[Dictionary[C[j][k]]])
                if(Students[i] in Survey[Dictionary[C[j][k]]][2]):      #是交心朋友
                    CS+=0.06
                elif(Students[i] in Survey[Dictionary[C[j][k]]][3]):    #是好朋友
                    CS+=0.03
                else:
                    CS-=0.02                                            #是普通同学
            
                if(C[j][k] in Survey[Dictionary[Students[i]]][2]):
                    CS+=0.06
                elif(C[j][k] in Survey[Dictionary[Students[i]]][3]):    
                    CS+=0.03
                else:
                    CS-=0.02 
        
            CS/=len(C[j])
        
            if(CS < 0):
                print("ERROR!!")
            elif(CS > 0.94):
                C[j].append(Students[i])
                break
            else:
                continue    
    C=[x for x in C if x]               #剔除空元素        

    #重新计算社团凝聚度
    Community_Cohesion = np.zeros(len(C))
    for i in range(len(C)):
        count=0
        if(len(C[i]) == 1):
            Community_Cohesion[i] = 1
            continue
        for j in range(len(C[i])):
            for k in range(j+1, len(C[i])):
                count+=1
                Community_Cohesion[i]+=cos_sim(HobPer[Dictionary[C[i][j]]],HobPer[Dictionary[C[i][k]]])
                if(C[i][j] in Survey[Dictionary[C[i][k]]][2]):      #是交心朋友
                    Community_Cohesion[i]+=0.06
                elif(C[i][j] in Survey[Dictionary[C[i][k]]][3]):    #是好朋友
                    Community_Cohesion[i]+=0.03
                else:
                    Community_Cohesion[i]-=0.02                     #是普通同学
            
                if(C[i][k] in Survey[Dictionary[C[i][j]]][2]):
                    Community_Cohesion[i]+=0.06
                elif(C[i][k] in Survey[Dictionary[C[i][j]]][3]):    
                    Community_Cohesion[i]+=0.03
                else:
                    Community_Cohesion[i]-=0.02
        Community_Cohesion[i]/=count
    
    #每个社团的兴趣倾向
    Hobby_of_Community = np.zeros(len(C)*len(Hobby),dtype='O').reshape(len(C),len(Hobby))
    for i in range(len(C)):
        for j in range(len(C[i])):
            Hobby_of_Community[i][0]+=Survey[Dictionary[C[i][j]]][4]    #运动指数
            Hobby_of_Community[i][1]+=Survey[Dictionary[C[i][j]]][5]    #学习指数
            Hobby_of_Community[i][2]+=Survey[Dictionary[C[i][j]]][6]    #娱乐指数
            Hobby_of_Community[i][3]+=Survey[Dictionary[C[i][j]]][7]    #游戏指数
    Copy_Hobby_of_Community = Hobby_of_Community.copy()      
    
    Class = np.zeros(len(C)*7,dtype='O').reshape(len(C),7)

    for i in range(len(Class)):
        Class[i][0] = i                 #群组名
        Class[i][1] = len(C[i])         #每个群组的人数
        for j in range(2,5):
            t = Copy_Hobby_of_Community[i].argmax()
            Class[i][j] = Dir_hobby[t]
            Copy_Hobby_of_Community[i][t] = -1
            
    #每个人的兴趣倾向
    Copy_HobPer = HobPer.copy()
    Hobby_Sort = np.zeros(len(Students)*3,dtype='O').reshape(len(Students),3)
    for i in range(len(Hobby_Sort)):
        for j in range(len(Hobby_Sort[i])):
            t = Copy_HobPer[i].argmax()
            Hobby_Sort[i][j] = Dir_hobby[t]
            Copy_HobPer[i][t] = -1
            
    #绘图
    nodes=[]
    links=[]
    categories=[]
    for i in range(len(C)):
        t = {'凝聚度 '+str(round(Community_Cohesion[i],4))}
        palyer={}
        palyer["name"]="社团"+str(i)
        palyer["symbolSize"]=15
        palyer["value"]=t
        palyer["category"] = i
        categories.append({"name": "社团"+str(i)+' '+Class[i][2]+' '+Class[i][3]+' '+Class[i][4]})
        if palyer not in nodes:
            nodes.append(palyer)
        
        for j in range(len(C[i])):
            t2 = {'1.'+Hobby_Sort[Dictionary[C[i][j]]][0]+' 2.'+Hobby_Sort[Dictionary[C[i][j]]][1]+' 3.'+Hobby_Sort[Dictionary[C[i][j]]][2]+(j==len(C[i])-1)*'\n'}
            palyer2={}
            palyer2["name"]=C[i][j]
            palyer2["symbolSize"]=10
            palyer2["value"]=t2
            palyer2["category"] = i
        
            if palyer2 not in nodes:
                nodes.append(palyer2)

    linestyle_opts1=opts.LineStyleOpts(is_show=True,width=1,opacity=0.1,type_="solid", color="black")
    linestyle_opts2=opts.LineStyleOpts(is_show=True,width=1,opacity=0.3,type_="solid", color="red")
    for i in range(len(C)):
        for j in range(len(C[i])):
            links.append({"source": "社团"+str(i), "target": C[i][j],"lineStyle":linestyle_opts1})
            links.append({"source": C[i][j], "target": Survey[Dictionary[C[i][j]]][2], "value":'交心朋友',"lineStyle":linestyle_opts2})
            links.append({"source": C[i][j], "target": Survey[Dictionary[C[i][j]]][3], "value":'好朋友'})

    toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="right")

    graph= (Graph(init_opts=opts.InitOpts(width="1800px", height="900px")).add("", nodes, links, categories=categories,
             layout="force", repulsion=50).set_global_opts(title_opts=opts.TitleOpts("暨南大学\n人际关系图"),toolbox_opts=toolbox_opts))

    graph.render("人际关系图.html")
    
    webbrowser.open_new_tab('人际关系图.html')


if __name__ == '__main__':
    main()
