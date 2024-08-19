from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3

def safe_find_text(driver, selector, by=By.CSS_SELECTOR, default_value=""):
    try:
        element = driver.find_element(by, selector)
        if element:
            return element.text.strip()
        else:
            return default_value
    except Exception as e:
        # print(f"Error occurred while finding text: {e}")
        return default_value

def extract_and_save_job_data(cursor, driver, url):
    try:
        driver.get(url)

        # 必要なデータを取得するためのセレクタを設定
        job_data = {
            "url": url,
            "kjNo": safe_find_text(driver, '[class="m05"][name="kjNo"][id="ID_kjNo"]'),
            "uktkYmd": safe_find_text(driver, '[name="uktkYmd"]'),
            "shkiKigenHi": safe_find_text(driver, '[name="shkiKigenHi"]'),
            "juriAtsh": safe_find_text(driver, '[name="juriAtsh"]'),
            "kjKbn": safe_find_text(driver, '[class="m05"][name="kjKbn"][id="ID_kjKbn"]'),
            "onlinJishuOboUktkKahi": safe_find_text(driver, '[name="onlinJishuOboUktkKahi"]'),
            "sngBrui": safe_find_text(driver, '[name="sngBrui"]'),
            "tryKoyoKibo": safe_find_text(driver, '[name="tryKoyoKibo"]'),
            "jgshNo": safe_find_text(driver, '[name="jgshNo"]'),
            "jgshMeiKana": safe_find_text(driver, '[name="jgshMeiKana"]'),
            "jgshMei": safe_find_text(driver, '[name="jgshMei"]'),
            "szciYbn": safe_find_text(driver, '[name="szciYbn"]'),
            "szci": safe_find_text(driver, '[name="szci"]'),
            "sksu": safe_find_text(driver, '[name="sksu"]'),
            "shigotoNy": safe_find_text(driver, '[name="shigotoNy"]'),
            "koyoKeitai": safe_find_text(driver, '[name="koyoKeitai"]'),
            "hakenUkeoiToShgKeitai": safe_find_text(driver, '[name="hakenUkeoiToShgKeitai"]'),
            "hakenUkeoiToRdsha": safe_find_text(driver, '[name="hakenUkeoiToRdsha"]'),
            "koyoKikan": safe_find_text(driver, '[name="koyoKikan"]'),
            "shgBs": safe_find_text(driver, '[name="shgBs"]'),
            "shgBsYubinNo": safe_find_text(driver, '[name="shgBsYubinNo"]'),
            "shgBsJusho": safe_find_text(driver, '[name="shgBsJusho"]'),
            "shgBsMyorEki": safe_find_text(driver, '[name="shgBsMyorEki"]'),
            "shgBsKotsuShudan": safe_find_text(driver, '[name="shgBsKotsuShudan"]'),
            "shgBsShyoJn": safe_find_text(driver, '[name="shgBsShyoJn"]'),
            "shgBsKitsuTsak": safe_find_text(driver, '[name="shgBsKitsuTsak"]'),
            "mycarTskn": safe_find_text(driver, '[name="mycarTskn"]'),
            "tenkinNoKnsi": safe_find_text(driver, '[name="tenkinNoKnsi"]'),
            "nenreiSegn": safe_find_text(driver, '[name="nenreiSegn"]'),
            "nenreiSegnHanni": safe_find_text(driver, '[name="nenreiSegnHanni"]'),
            "nenreiSegnGaitoJiyu": safe_find_text(driver, '[name="nenreiSegnGaitoJiyu"]'),
            "nenreiSegnNoRy": safe_find_text(driver, '[name="nenreiSegnNoRy"]'),
            "grki": safe_find_text(driver, '[name="grki"]'),
            "hynaKiknt": safe_find_text(driver, '[name="hynaKiknt"]'),
            "hynaKikntShsi": safe_find_text(driver, '[name="hynaKikntShsi"]'),
            "hynaMenkyoSkku": safe_find_text(driver, '[name="hynaMenkyoSkku"]'),
            "trialKikan": safe_find_text(driver, '[name="trialKikan"]'),
            "chgn": safe_find_text(driver, '[name="chgn"]'),
            "khky": safe_find_text(driver, '[name="khky"]'),
            "tgktNiShwrTat": safe_find_text(driver, '[name="tgktNiShwrTat"]'),
            "koteiZngyKbn": safe_find_text(driver, '[name="koteiZngyKbn"]'),
            "thkinRodoNissu": safe_find_text(driver, '[name="thkinRodoNissu"]'),
            "chgnKeitaiToKbn": safe_find_text(driver, '[name="chgnKeitaiToKbn"]'),
            "tsknTat": safe_find_text(driver, '[name="tsknTat"]'),
            "chgnSkbi": safe_find_text(driver, '[name="chgnSkbi"]'),
            "chgnSrbi": safe_find_text(driver, '[name="chgnSrbi"]'),
            "chgnSrbiTsuki": safe_find_text(driver, '[name="chgnSrbiTsuki"]'),
            "chgnSrbiHi": safe_find_text(driver, '[name="chgnSrbiHi"]'),
            "shokyuSd": safe_find_text(driver, '[name="shokyuSd"]'),
            "shokyuMaeNendoJisseki": safe_find_text(driver, '[name="shokyuMaeNendoJisseki"]'),
            "sokkgSkrt": safe_find_text(driver, '[name="sokkgSkrt"]'),
            "shoyoSdNoUmu": safe_find_text(driver, '[name="shoyoSdNoUmu"]'),
            "shoyoMaeNendoUmu": safe_find_text(driver, '[name="shoyoMaeNendoUmu"]'),
            "shoyoMaeNendKaisu": safe_find_text(driver, '[name="shoyoMaeNendKaisu"]'),
            "shoyoKingaku": safe_find_text(driver, '[name="shoyoKingaku"]'),
            "shgJn1": safe_find_text(driver, '[name="shgJn1"]'),
            "jkgiRodoJn": safe_find_text(driver, '[name="jkgiRodoJn"]'),
            "thkinJkgiRodoJn": safe_find_text(driver, '[name="thkinJkgiRodoJn"]'),
            "sanrokuKyotei": safe_find_text(driver, '[name="sanrokuKyotei"]'),
            "kyukeiJn": safe_find_text(driver, '[name="kyukeiJn"]'),
            "nenkanKjsu": safe_find_text(driver, '[name="nenkanKjsu"]'),
            "kyjs": safe_find_text(driver, '[name="kyjs"]'),
            "shukFtskSei": safe_find_text(driver, '[name="shukFtskSei"]'),
            "kyjsSnta": safe_find_text(driver, '[name="kyjsSnta"]'),
            "nenjiYukyu": safe_find_text(driver, '[name="nenjiYukyu"]'),
            "knyHoken": safe_find_text(driver, '[name="knyHoken"]'),
            "tskinKsi": safe_find_text(driver, '[name="tskinKsi"]'),
            "tskinSd": safe_find_text(driver, '[name="tskinSd"]'),
            "tskinSdKinzokuNensu": safe_find_text(driver, '[name="tskinSdKinzokuNensu"]'),
            "tnsei": safe_find_text(driver, '[name="tnsei"]'),
            "tnseiTeinenNenrei": safe_find_text(driver, '[name="tnseiTeinenNenrei"]'),
            "saiKoyoSd": safe_find_text(driver, '[name="saiKoyoSd"]'),
            "kmec": safe_find_text(driver, '[name="kmec"]'),
            "nkj": safe_find_text(driver, '[name="nkj"]'),
            "nkjTkjk": safe_find_text(driver, '[name="nkjTkjk"]'),
            "riyoKanoTkjShst": safe_find_text(driver, '[name="riyoKanoTkjShst"]'),
            "jgisKigyoZentai": safe_find_text(driver, '[name="jgisKigyoZentai"]'),
            "jgisShgBs": safe_find_text(driver, '[name="jgisShgBs"]'),
            "jgisUchiJosei": safe_find_text(driver, '[name="jgisUchiJosei"]'),
            "jgisUchiPart": safe_find_text(driver, '[name="jgisUchiPart"]'),
            "setsuritsuNen": safe_find_text(driver, '[name="setsuritsuNen"]'),
            "shkn": safe_find_text(driver, '[name="shkn"]'),
            "rodoKumiai": safe_find_text(driver, '[name="rodoKumiai"]'),
            "jigyoNy": safe_find_text(driver, '[name="jigyoNy"]'),
            "kaishaNoTokucho": safe_find_text(driver, '[name="kaishaNoTokucho"]'),
            "yshk": safe_find_text(driver, '[name="yshk"]'),
            "dhshaMei": safe_find_text(driver, '[name="dhshaMei"]'),
            "hoNinNo": safe_find_text(driver, '[name="hoNinNo"]'),
            "fltmShgKisoku": safe_find_text(driver, '[name="fltmShgKisoku"]'),
            "partShgKisoku": safe_find_text(driver, '[name="partShgKisoku"]'),
            "ikujiKyugyoStkJisseki": safe_find_text(driver, '[name="ikujiKyugyoStkJisseki"]'),
            "kaigoKyugyoStkJisseki": safe_find_text(driver, '[name="kaigoKyugyoStkJisseki"]'),
            "kangoKyukaStkJisseki": safe_find_text(driver, '[name="kangoKyukaStkJisseki"]'),
            "gkjnKoyoJisseki": safe_find_text(driver, '[name="gkjnKoyoJisseki"]'),
            "saiyoNinsu": safe_find_text(driver, '[name="saiyoNinsu"]'),
            "boshuRy": safe_find_text(driver, '[name="boshuRy"]'),
            "selectHoho": safe_find_text(driver, '[name="selectHoho"]'),
            "selectKekkaTsuch": safe_find_text(driver, '[name="selectKekkaTsuch"]'),
            "shoruiSelectKekka": safe_find_text(driver, '[name="shoruiSelectKekka"]'),
            "mensetsuSelectKekka": safe_find_text(driver, '[name="mensetsuSelectKekka"]'),
            "ksshEnoTsuchiHoho": safe_find_text(driver, '[name="ksshEnoTsuchiHoho"]'),
            "selectNichijiTo": safe_find_text(driver, '[name="selectNichijiTo"]'),
            "selectBsYubinNo": safe_find_text(driver, '[name="selectBsYubinNo"]'),
            "selectBsJusho": safe_find_text(driver, '[name="selectBsJusho"]'),
            "selectBsMyorEki": safe_find_text(driver, '[name="selectBsMyorEki"]'),
            "selectBsMyorEkiKotsuShudan": safe_find_text(driver, '[name="selectBsMyorEkiKotsuShudan"]'),
            "selectBsShyoJn": safe_find_text(driver, '[name="selectBsShyoJn"]'),
            "oboShoruitou": safe_find_text(driver, '[name="oboShoruitou"]'),
            "oboShoruiNoSofuHoho": safe_find_text(driver, '[name="oboShoruiNoSofuHoho"]'),
            "yusoNoSofuBsYubinNo": safe_find_text(driver, '[name="yusoNoSofuBsYubinNo"]'),
            "yusoNoSofuBsJusho": safe_find_text(driver, '[name="yusoNoSofuBsJusho"]'),
            "obohen": safe_find_text(driver, '[name="obohen"]'),
            "ttsYkm": safe_find_text(driver, '[name="ttsYkm"]'),
            "ttsTts": safe_find_text(driver, '[name="ttsTts"]'),
            "ttsTel": safe_find_text(driver, '[name="ttsTel"]'),
            "ttsFax": safe_find_text(driver, '[name="ttsFax"]'),
            "kjTkjk": safe_find_text(driver, '[name="kjTkjk"]'),
            "shokumuKyuSd": safe_find_text(driver, '[name="shokumuKyuSd"]'),
            "shokumuKyuSdNoNy": safe_find_text(driver, '[name="shokumuKyuSdNoNy"]'),
            "fukushokuSd": safe_find_text(driver, '[name="fukushokuSd"]'),
            "fukushokuSdNoNy": safe_find_text(driver, '[name="fukushokuSdNoNy"]')
        }


        cursor.execute('''
        INSERT OR REPLACE INTO hw_jobs (
            url, kjNo, uktkYmd, shkiKigenHi, juriAtsh, kjKbn, onlinJishuOboUktkKahi, sngBrui, tryKoyoKibo, jgshNo,
            jgshMeiKana, jgshMei, szciYbn, szci, sksu, shigotoNy, koyoKeitai, hakenUkeoiToShgKeitai, hakenUkeoiToRdsha,
            koyoKikan, shgBs, shgBsYubinNo, shgBsJusho, shgBsMyorEki, shgBsKotsuShudan, shgBsShyoJn, shgBsKitsuTsak,
            mycarTskn, tenkinNoKnsi, nenreiSegn, nenreiSegnHanni, nenreiSegnGaitoJiyu, nenreiSegnNoRy, grki, hynaKiknt,
            hynaKikntShsi, hynaMenkyoSkku, trialKikan, chgn, khky, tgktNiShwrTat, koteiZngyKbn, thkinRodoNissu, chgnKeitaiToKbn,
            tsknTat, chgnSkbi, chgnSrbi, chgnSrbiTsuki, chgnSrbiHi, shokyuSd, shokyuMaeNendoJisseki, sokkgSkrt, shoyoSdNoUmu,
            shoyoMaeNendoUmu, shoyoMaeNendKaisu, shoyoKingaku, shgJn1, jkgiRodoJn, thkinJkgiRodoJn, sanrokuKyotei, kyukeiJn,
            nenkanKjsu, kyjs, shukFtskSei, kyjsSnta, nenjiYukyu, knyHoken, tskinKsi, tskinSd, tskinSdKinzokuNensu, tnsei,
            tnseiTeinenNenrei, saiKoyoSd, kmec, nkj, nkjTkjk, riyoKanoTkjShst, jgisKigyoZentai, jgisShgBs, jgisUchiJosei,
            jgisUchiPart, setsuritsuNen, shkn, rodoKumiai, jigyoNy, kaishaNoTokucho, yshk, dhshaMei, hoNinNo, fltmShgKisoku,
            partShgKisoku, ikujiKyugyoStkJisseki, kaigoKyugyoStkJisseki, kangoKyukaStkJisseki, gkjnKoyoJisseki, saiyoNinsu,
            boshuRy, selectHoho, selectKekkaTsuch, shoruiSelectKekka, mensetsuSelectKekka, ksshEnoTsuchiHoho, selectNichijiTo,
            selectBsYubinNo, selectBsJusho, selectBsMyorEki, selectBsMyorEkiKotsuShudan, selectBsShyoJn, oboShoruitou,
            oboShoruiNoSofuHoho, yusoNoSofuBsYubinNo, yusoNoSofuBsJusho, obohen, ttsYkm, ttsTts, ttsTel, ttsFax, kjTkjk,
            shokumuKyuSd, shokumuKyuSdNoNy, fukushokuSd, fukushokuSdNoNy
        ) VALUES (
            :url, :kjNo, :uktkYmd, :shkiKigenHi, :juriAtsh, :kjKbn, :onlinJishuOboUktkKahi, :sngBrui, :tryKoyoKibo, :jgshNo,
            :jgshMeiKana, :jgshMei, :szciYbn, :szci, :sksu, :shigotoNy, :koyoKeitai, :hakenUkeoiToShgKeitai, :hakenUkeoiToRdsha,
            :koyoKikan, :shgBs, :shgBsYubinNo, :shgBsJusho, :shgBsMyorEki, :shgBsKotsuShudan, :shgBsShyoJn, :shgBsKitsuTsak,
            :mycarTskn, :tenkinNoKnsi, :nenreiSegn, :nenreiSegnHanni, :nenreiSegnGaitoJiyu, :nenreiSegnNoRy, :grki, :hynaKiknt,
            :hynaKikntShsi, :hynaMenkyoSkku, :trialKikan, :chgn, :khky, :tgktNiShwrTat, :koteiZngyKbn, :thkinRodoNissu, :chgnKeitaiToKbn,
            :tsknTat, :chgnSkbi, :chgnSrbi, :chgnSrbiTsuki, :chgnSrbiHi, :shokyuSd, :shokyuMaeNendoJisseki, :sokkgSkrt, :shoyoSdNoUmu,
            :shoyoMaeNendoUmu, :shoyoMaeNendKaisu, :shoyoKingaku, :shgJn1, :jkgiRodoJn, :thkinJkgiRodoJn, :sanrokuKyotei, :kyukeiJn,
            :nenkanKjsu, :kyjs, :shukFtskSei, :kyjsSnta, :nenjiYukyu, :knyHoken, :tskinKsi, :tskinSd, :tskinSdKinzokuNensu, :tnsei,
            :tnseiTeinenNenrei, :saiKoyoSd, :kmec, :nkj, :nkjTkjk, :riyoKanoTkjShst, :jgisKigyoZentai, :jgisShgBs, :jgisUchiJosei,
            :jgisUchiPart, :setsuritsuNen, :shkn, :rodoKumiai, :jigyoNy, :kaishaNoTokucho, :yshk, :dhshaMei, :hoNinNo, :fltmShgKisoku,
            :partShgKisoku, :ikujiKyugyoStkJisseki, :kaigoKyugyoStkJisseki, :kangoKyukaStkJisseki, :gkjnKoyoJisseki, :saiyoNinsu,
            :boshuRy, :selectHoho, :selectKekkaTsuch, :shoruiSelectKekka, :mensetsuSelectKekka, :ksshEnoTsuchiHoho, :selectNichijiTo,
            :selectBsYubinNo, :selectBsJusho, :selectBsMyorEki, :selectBsMyorEkiKotsuShudan, :selectBsShyoJn, :oboShoruitou,
            :oboShoruiNoSofuHoho, :yusoNoSofuBsYubinNo, :yusoNoSofuBsJusho, :obohen, :ttsYkm, :ttsTts, :ttsTel, :ttsFax, :kjTkjk,
            :shokumuKyuSd, :shokumuKyuSdNoNy, :fukushokuSd, :fukushokuSdNoNy
        )
        ''', job_data)

        cursor.connection.commit()
        print(f"Data inserted for {url}")

    except sqlite3.Error as e:
        print(f"SQL Error: {e}")

    except Exception as e:
        print(f"Error processing {url}: {e}")