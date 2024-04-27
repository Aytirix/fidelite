from tools import *

def connect_bdd():
    try:
        sql = mysql.connector.connect(host=os.getenv("db_host"), user=os.getenv("db_user"), passwd=os.getenv("db_password"), database=os.getenv("db_database"))
        return sql
    except Exception as e:
        print(Style.BRIGHT,Fore.RED, "ERREUR : Connexion à la base de données distrokid échoué\n"+str(e)+"\n",Style.RESET_ALL)
        return False
    
# Décorateur pour se connecter à la base de données
def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sql = connect_bdd()
        if sql:
            try:
                result = func(sql, *args, **kwargs)
            finally:
                if sql.is_connected():
                    sql.close()
            return result
        else:
            return False
    return wrapper


@with_db_connection
def get_config(sql, nom):
    try:
        cursor = sql.cursor()
        cursor.execute("SELECT `VALEUR` FROM `CONFIG` WHERE `NOM` like %s", [nom])
        result = cursor.fetchone()
        if result == None:
            return False
        return result[0]
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération de la config de la table config\n{str(e)}\n", "red")
        return False

def test_Proxy(proxy, msg=True):
    try:
        proxy = {"http": proxy, "https": proxy}
        r = requests.get("https://google.com", proxies=proxy, timeout=5)
        if r.status_code == 200:
            return True
        else:
            print_msg(f"PROXY Votre ip n'est pas dans la whitelist de votre proxy : {proxy}", "red")
            return False
    except Exception as e:
        if msg:
            print_msg(f"PROXY Impossible d'établir une connexion avec le proxy : {proxy}", "red")
        return False

@with_db_connection
def GetAllProxy(sql):
    try:
        cursor = sql.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `PROXY`")
        result = cursor.fetchall()
        if result == []:
            return False
        if not test_Proxy(random.choice(result)["PROXY"]):
            stop()
        return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération d'une liste de proxy dans la table PROXY\n{str(e)}\n", "red")
        return False

@with_db_connection
def get_plateformes(sql, actif=None):
    try:
        cursor = sql.cursor(dictionary=True)

        if actif == None:
            cursor.execute("SELECT * FROM `PLATEFORMES`")
        else:
            cursor.execute("SELECT * FROM `PLATEFORMES` WHERE `ACTIF` = %s", [actif])
        result = cursor.fetchall()
        if result == None:
            return False
        return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération des plateformes de la table plateformes\n{str(e)}\n", "red")
        return False
    
@with_db_connection
def get_compte_valide(sql):
    try:
        cursor = sql.cursor(dictionary=True)
        cursor.execute("SELECT `c`.ID, `c`.EMAIL, `c`.PASSWORD FROM `COMPTES` `c` JOIN `ASSO_COMPTE_PLATEFORME` `acp` ON `c`.`ID` = `acp`.`ID_COMPTE` WHERE `acp`.`ACTIF` = 1")
        result = cursor.fetchall()
        if result == None:
            return False
        # mettre les clef en minuscule
        result = [{k.lower(): v for k, v in d.items()} for d in result]
        return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération des comptes valides de la table comptes\n{str(e)}\n", "red")
        return False
    
@with_db_connection
def get_compte_non_verifie(sql):
    try:
        sql = connect_bdd()
        if sql:
            cursor = sql.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT c.ID, c.EMAIL, c.PASSWORD, acp.ACTIF FROM COMPTES c LEFT JOIN ASSO_COMPTE_PLATEFORME acp ON c.ID = acp.ID_COMPTE WHERE acp.ACTIF IS NULL OR acp.ID_COMPTE IS NULL ORDER BY `acp`.`ACTIF` DESC")
            result = cursor.fetchall()
            if result == None:
                return False
            # mettre les clef en minuscule
            result = [{k.lower(): v for k, v in d.items()} for d in result]
            return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération des comptes non vérifié de la table comptes\n{str(e)}\n", "red")
        return False

@with_db_connection
def add_comptes(sql, email, password):
    try:
        cursor = sql.cursor()
        cursor.execute("INSERT INTO `COMPTES` (`EMAIL`, `PASSWORD`) VALUES (%s, %s)", [email, password])
        sql.commit()
        return cursor.lastrowid
    # Si le compte existe déjà
    except mysql.connector.errors.IntegrityError as e:
        # retourne l'id du compte
        cursor.execute("SELECT `ID` FROM `COMPTES` WHERE `EMAIL` = %s AND `PASSWORD` = %s", [email, password])
        result = cursor.fetchone()
        if result == None:
            return False
        return result[0]
    except Exception as e:
        print_msg(f"SQL ERREUR : Ajout du compte {email} dans la table comptes\n{str(e)}\n", "red")
        return False

@with_db_connection
def add_asso_compte_plateforme(sql, id_compte, nom_plateforme, actif, point, code_point, message):
    try:
        if "timed out after" in str(message):
            message = "timed out after"+message.split("timed out after")[1]
        cursor = sql.cursor()
        cursor.execute("INSERT INTO `ASSO_COMPTE_PLATEFORME` (`ID_COMPTE`, `NOM_PLATEFORME`, `ACTIF`, `POINT`, `CODE_POINT`, `MESSAGE`) VALUES (%s, %s, %s, %s, %s, %s)", [id_compte, nom_plateforme, actif, point, code_point, message])
        sql.commit()
        return True
    except Exception as e:
        print_msg(f"SQL ERREUR : Ajout de l'association compte/plateforme {id_compte}/{nom_plateforme} dans la table asso_compte_plateforme\n{str(e)}\n", "red")
        return False
    
@with_db_connection
def get_id_compte_email_password(sql, email, password):
    try:
        cursor = sql.cursor()
        cursor.execute("SELECT ID FROM `COMPTES` WHERE `EMAIL` = %s AND `PASSWORD` = %s", [email, password])
        result = cursor.fetchone()
        if result == None:
            return ""
        return result[0]
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération du compte {email} dans la table comptes\n{str(e)}\n", "red")
        return False

@with_db_connection
def update_asso_compte_plateforme(sql, id_compte, nom_plateforme, actif = None, point = None, code_point = None, message = None):
    try:
        cursor = sql.cursor()
        prepare = "UPDATE `ASSO_COMPTE_PLATEFORME` SET LAST_CHECK = NOW(), "
        args = []

        if actif != None:
            prepare += "`ACTIF` = %s"
            args.append(actif)
        
        if point != None:
            if len(args) > 0:
                prepare += ", "
            prepare += "`POINT` = %s"
            args.append(point)

        if code_point != None:
            code_point = code_point[:10]
            if len(args) > 0:
                prepare += ", "
            prepare += "`CODE_POINT` = %s"
            args.append(code_point)

        if message != None:
            message = message[:255]  
            if len(args) > 0:
                prepare += ", "
            prepare += "`MESSAGE` = %s"
            args.append(message)
        
        prepare += " WHERE `ID_COMPTE` = %s AND `NOM_PLATEFORME` = %s"
        args.append(id_compte)
        args.append(nom_plateforme)

        cursor.execute(prepare, args)
        sql.commit()
        return True
    except Exception as e:
        print_msg(f"SQL ERREUR : Modification de l'association compte/plateforme {id_compte}/{nom_plateforme} dans la table asso_compte_plateforme\n{str(e)}\n", "red")
        return False
    
@with_db_connection
def check_asso_compte_plateforme(sql, email, password):
    try:
        cursor = sql.cursor(dictionary=True)
        cursor.execute("SELECT `ASSO_COMPTE_PLATEFORME`.`ID_COMPTE`, `ASSO_COMPTE_PLATEFORME`.`NOM_PLATEFORME`, `ASSO_COMPTE_PLATEFORME`.`ACTIF`, `ASSO_COMPTE_PLATEFORME`.`POINT`, `ASSO_COMPTE_PLATEFORME`.`LAST_CHECK` FROM `ASSO_COMPTE_PLATEFORME` INNER JOIN `COMPTES` ON `ASSO_COMPTE_PLATEFORME`.`ID_COMPTE` = `COMPTES`.`ID` WHERE `COMPTES`.`EMAIL` = %s AND `COMPTES`.`PASSWORD` = %s", [email, password])
        result = cursor.fetchall()
        if result == None:
            return False
        return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Vérification de l'association compte/plateforme {email} dans la table asso_compte_plateforme\n{str(e)}\n", "red")
        return False

@with_db_connection
def add_cookie(sql, cookie, plateforme, user_agent, proxy):
    try:
        cursor = sql.cursor()
        date = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO `COOKIES` (`PLATEFORME`, `USER_AGENT`, `PROXY`, `COOKIE`, `LAST_CHECK`) VALUES (%s, %s, %s, %s, %s)", [plateforme, user_agent, proxy, cookie, date])
        sql.commit()
        return True
    except Exception as e:
        print_msg(f"SQL ERREUR : Ajout du cookie {cookie} dans la table cookies\n{str(e)}\n", "red")
        return False
    
@with_db_connection
def get_cookies(sql, plateforme):
    try:
        cursor = sql.cursor(dictionary=True)
        sql.start_transaction()
        # il faut que le last_check soit supérieur à 5 minutes
        cursor.execute("SELECT * FROM `COOKIES` WHERE `PLATEFORME` = %s AND `LAST_CHECK` < DATE_SUB(NOW(), INTERVAL 5 MINUTE) ORDER BY `LAST_CHECK` ASC LIMIT 1 FOR UPDATE", [plateforme])
        result = cursor.fetchone()
        if not result:
            return False
        cursor.execute("UPDATE `COOKIES` SET `LAST_CHECK` = NOW() WHERE `ID` = %s", [result["ID"]])
        sql.commit()
        result["COOKIE"] = deserialize_from_json(result["COOKIE"])
        return result
    except Exception as e:
        print_msg(f"SQL ERREUR : Récupération des cookies de la table cookies\n{str(e)}\n", "red")
        return False

@with_db_connection
def delete_cookie(sql, ID):
    try:
        cursor = sql.cursor()
        cursor.execute("DELETE FROM `COOKIES` WHERE `ID` = %s", [ID])
        sql.commit()
        return True
    except Exception as e:
        print_msg(f"SQL ERREUR : Suppression du cookie {ID} dans la table cookies\n{str(e)}\n", "red")
        return False

@with_db_connection
def get_and_delete_random_cookie(sql, plateforme):
    try:
        cursor = sql.cursor(dictionary=True)
        try:
            # Début de la transaction
            sql.start_transaction()

            # Sélectionne un cookie aléatoire pour la plateforme spécifiée
            cursor.execute("SELECT * FROM `COOKIES` WHERE `PLATEFORME` = %s LIMIT 5 FOR UPDATE", (plateforme,))
            result = cursor.fetchall()

            if not result:
                return None

            # Choix aléatoire d'un cookie parmi les résultats
            selected_cookie = random.choice(result)
            selected_cookie['COOKIE'] = deserialize_from_json(selected_cookie['COOKIE'])

            # Suppression du cookie sélectionné
            cursor.execute("DELETE FROM `COOKIES` WHERE `ID` = %s", (selected_cookie['ID'],))
            sql.commit()
            
            return selected_cookie

        except Exception as e:
            # En cas d'erreur, annulation de la transaction
            sql.rollback()
            raise e

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return None
    finally:
        if sql.is_connected():
            cursor.close()
            sql.close()

@with_db_connection
def get_proxy_random(sql):
    try:
        cursor = sql.cursor(dictionary=True)
        try:
            # Début de la transaction
            sql.start_transaction()

            # Sélectionne un cookie aléatoire pour la plateforme spécifiée
            cursor.execute("SELECT * FROM `PROXY` WHERE `LAST_CHECK` < DATE_SUB(NOW(), INTERVAL 5 MINUTE) ORDER BY `LAST_CHECK` ASC LIMIT 1 FOR UPDATE")
            result = cursor.fetchone()

            if not result:
                return None

            # Mise à jour du proxy sélectionné
            cursor.execute("UPDATE `PROXY` SET `LAST_CHECK` = NOW() WHERE `PROXY` = %s", (result['PROXY'],))
            sql.commit()
            
            return result['PROXY']

        except Exception as e:
            # En cas d'erreur, annulation de la transaction
            sql.rollback()
            raise e

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return None
    finally:
        if sql.is_connected():
            cursor.close()
            sql.close()

@with_db_connection
def update_last_check_proxy(sql, proxy, date=datetime.datetime.now()):
    try:
        cursor = sql.cursor()
        cursor.execute("UPDATE `PROXY` SET `LAST_CHECK` = %s WHERE `PROXY` = %s", [date, proxy])
        sql.commit()
        return True
    except Exception as e:
        print_msg(f"SQL ERREUR : Mise à jour du proxy {proxy} dans la table proxy\n{str(e)}\n", "red")
        return False