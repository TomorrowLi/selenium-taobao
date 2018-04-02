import re
import MySQLdb
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
broser=webdriver.Chrome()

wait=WebDriverWait(broser, 10)
def search(table):
    try:
        broser.get('https://www.taobao.com')
        inputs = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        inputs.send_keys('美食')
        submit.click()
        total = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total'))
        )
        get_product(table)
        return total.text
    except TimeoutException:
        return search(table)
def next_page(page_number,table):
    try:
        inputs = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        inputs.clear()
        inputs.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number))
        )
        get_product(table)
    except TimeoutException:
        next_page(page_number,table)
def get_product(table):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html=broser.page_source
    doc=pq(html)
    items=doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product={
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text().replace('\n',''),
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text().replace('\n',''),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        inserttable(table, product['image'], product['price'], product['deal'], product['title'],product['shop'],product['location'])
#连接数据库 mysql
def connectDB():
        host="localhost"
        dbName="test"
        user="root"
        password=""
        #此处添加charset='utf8'是为了在数据库中显示中文，此编码必须与数据库的编码一致
        db=MySQLdb.connect(host,user,password,dbName,charset='utf8')
        return db
        cursorDB=db.cursor()
        return cursorDB

#创建表，SQL语言。CREATE TABLE IF NOT EXISTS 表示：表createTableName不存在时就创建
def creatTable(createTableName):
    createTableSql="CREATE TABLE IF NOT EXISTS "+ createTableName+"(image VARCHAR(255),price VARCHAR(255),deal  VARCHAR(255),title VARCHAR(255),shop VARCHAR(255),location VARCHAR(255))"
    DB_create=connectDB()
    print('链接数据库成功')
    cursor_create=DB_create.cursor()
    cursor_create.execute(createTableSql)
    DB_create.close()
    print('creat table '+createTableName+' successfully')
    return createTableName
#数据插入表中
def inserttable(insertTable,insertimages,insertprice,insertdeal,inserttitle,insertshop,insertloaction):
    insertContentSql="INSERT INTO "+insertTable+"(image,price,deal,title,shop,location)VALUES(%s,%s,%s,%s,%s,%s)"
#         insertContentSql="INSERT INTO "+insertTable+"(time,title,text,clicks)VALUES("+insertTime+" , "+insertTitle+" , "+insertText+" , "+insertClicks+")"


    DB_insert=connectDB()
    cursor_insert=DB_insert.cursor()
    cursor_insert.execute(insertContentSql,(insertimages,insertprice,insertdeal,inserttitle,insertshop,insertloaction))
    DB_insert.commit()
    DB_insert.close()
    print ('inert contents to  '+insertTable+' successfully')

def main():
    table = creatTable('yh1')
    print('创建表成功')
    total=search(table)
    total=int(re.compile('(\d+)').search(total).group(1))
    for i in range(2,total+1):
        next_page(i,table)
if __name__=='__main__':
    main()