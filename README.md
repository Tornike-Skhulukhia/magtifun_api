# მოდული საშუალებას გვაძლევს გავგზავნოთ შეტყობინებები magtifun.ge-ის გამოყენებით ჩვენი მომხმარებლის ნომრით.

![მაგთიფანის ლოგო](http://www.magtifun.ge/images/logo.gif)

## საჭირო ბიბლიოთეკები: requests & beautifulsoup4

### გამოყენების მაგალითი
```python
from magtifun_oop import MagtiFun

# from info import username, password

username = "მომხმარებელი"
password = "პაროლი"

# numbers და messages შეიძლება იყოს str ტიპის მონაცემები,
# თუ ერთ ნომერზე ვგზავნით 1 შეტყობინებას
numbers, messages = "591012340", "სალამი მაგთიფანიდან"

# ან სიები ერთი სიგრძით, საიდანაც პირველი შეტყობინება გაიგზავნება
# პირველ ნომერთან, მეორე მეორესთან და ა.შ.
numbers, messages = ["591012340"], ["სალამი მაგთიფანიდან"]

# მაგალითი
s = MagtiFun(username, password)

if s.login():
    print("წარმატებული ავტორიზაცია")

    # s.get_balance(); print("ბალანსი:", s.balance)

    if s.send_messages(numbers, messages):
        print("ყველა შეტყობინება წარმატებით გაიგზავნა")
    else:
        print("ზოგიერთი შეტყობინება ვერ გაიგზავნა, შეამოწმე log-ის ფაილი")
else:
    print("წარუმატებელი ავტორიზაცია")

```


### მუშაობის პრინციპი გარდა ფუნქციებისა, ასევე ახსნილია ვიდეოში:
[![ვიდეო](https://img.youtube.com/vi/mY4Y3llZHMY/0.jpg)](https://www.youtube.com/watch?v=mY4Y3llZHMY)
