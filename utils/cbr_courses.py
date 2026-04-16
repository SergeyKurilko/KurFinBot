import httpx
import xml.etree.ElementTree as ET


async def get_cbr_usd_course():
    """Получение курса доллара из ЦБР"""
    usd_value = None
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.cbr.ru/scripts/XML_daily.asp")
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            usd = root.find(".//Valute[CharCode='USD']")
            if usd is not None:
                usd_value_str = usd.find("Value").text.replace(",", ".")
                usd_value = int(float(usd_value_str))
    return usd_value


