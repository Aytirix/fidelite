from administration import administration
from plateformes.KFC import KFC
from tools import *
from menu import *
from bdd import *
import threading

os.system("cls")

connect_bdd()

plateformes = get_plateformes(actif=1)
if not plateformes:
    print_msg("ERREUR, Impossible de récupérer les plateformes", "red")
    exit()

force_check = True
combo_list, force_check = choix_compte()
# combo_list = [{"email": "zejfze4e@ezfze.fr", "password": "zefzefzef"}]
# combo_list = [{"email": "uthewarrior@gmail.com", "password": "AzErTy59!"}]  
# print_msg("Nombre de compte à checker : " + str(len(combo_list)), "green")

proxys = GetAllProxy()

# Généer les cookies de kfc
# KFC().generate_cookie(proxys, 1)
for i in range(0, 1):
    cookie_thread = threading.Thread(target=KFC().generate_cookie, args=(proxys, i))
    cookie_thread.daemon = True
    cookie_thread.start()
    time.sleep(random.randint(1, 2))
# time.sleep(10)
thread_list = []

num = 0
for combo in combo_list:
        proxy = None
        while not proxy:
            proxy = get_proxy_random()
        num += 1
        app = administration(str(f"{num}/{len(combo_list)}"), "", combo["email"], combo["password"], plateformes, proxy, force_check=force_check)
        app.start()
        thread_list.append(app)
        while len(thread_list) >= int(os.getenv("max_chromedriver")):
            for thread in thread_list.copy():
                if not thread.is_alive():
                    thread_list.remove(thread)
        time.sleep(5)

for thread in thread_list:
    thread.join()
print_msg("Fin du programme", "green")