import qrcode
from PIL import Image
from utils.models import User

logo_link = 'qrs/logo1.png'

logo = Image.open(logo_link)

basewidth = 50

wpercent = (basewidth / float(logo.size[0]))
hsize = int((float(logo.size[1]) * float(wpercent)))
logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)


async def generate_and_save(user: User, data) -> str:
    qr_code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_code.add_data(data)
    qr_code.make()
    qr_img = qr_code.make_image().convert("RGB")

    pos = ((qr_img.size[0] - logo.size[0]) // 2,
           (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos)
    qr_img.save(f"qrs/{user.chat_id}_{user.id}.png")

    # img = qrcode.make(data)
    return f"qrs/{user.chat_id}_{user.id}.png"
