import pyotp
import qrcode

t=pyotp.TOTP('3232323232323232')

name=input("Enter name")
issuer_name='Google'
auth_str=t.provisioning_uri(name,issuer_name)
print(auth_str)
img=qrcode.make(auth_str)
display(img)
print(t.now())