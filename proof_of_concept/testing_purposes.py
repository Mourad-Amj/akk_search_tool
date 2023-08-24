# Streamlit proof of concept
# Run this with 
# python -m streamlit run proof_of_concept/app.py

# imports
import streamlit as st
import pandas as pd
import io
import xlsxwriter

#DO NOT USE
#import SessionState

from sentence_transformers import SentenceTransformer, util
import datetime


# initialization
st.title("PoC: lachambre.be custom search engine")


@st.cache_data
def load_data():
    database=[{'id':  "55K3152",
            'title':    "Projet de loi relatif à l'approche administrative communale, à la mise en place d'une enquête d'intégrité communale et portant création d'une Direction chargée de l'Évaluation de l'Intégrité pour les Pouvoirs publics.",
            'text': "Ces dernières années, la criminalité organisée et déstabilisante n’a cessé de s’immiscer dans le tissu social. Certaines entreprises sont utilisées comme couverture pour le blanchiment d’argent et le commerce illégal. Les villes et les communes détectent souvent ces problèmes ou ces circonstances à un stade précoce. Cependant, au niveau local, le cadre juridique actuel n’est pas suffisant pour traiter ces problèmes de manière adéquate. La transmission des informations pertinentes aux pouvoirs locaux est ainsi souvent incomplète et/ ou fragmentée. Il semble également difficile pour les pouvoirs locaux de faire appliquer certaines mesures de police administrative. Ce nouveau projet de loi relatif à l’approche administrative communale fournit un cadre juridique clair et complet à cet égard. Le présent projet de loi vise à fournir aux pouvoirs locaux une base juridique spécifique pour prendre des mesures en vue d’empêcher la criminalité déstabilisante. Le projet de loi prévoit notamment la possibilité pour les pouvoirs locaux de mener une enquête d’intégrité approfondie sur l’implantation ou l’exploitation d’établissements accessibles au public dans le cadre de certains secteurs et activités économiques et prévoit, sur base du résultat de cette enquête, de refuser, suspendre ou abroger le permis d’implantation ou d’exploitation ou de fermer l’établissement. En outre, le projet de loi crée une Direction chargée de l’Évaluation de l’Intégrité pour les Pouvoirs publics (DEIPP) qui aura accès aux données et informations pertinentes pouvant être intégrées dans un avis aux pouvoirs locaux, prévoit un ensemble d’outils permettant de mieux faire respecter des mesures de police administratives comme les fermetures, et développe davantage les Centres d’Information et d’Expertise d’Arrondissement (CIEAR). Le projet de loi s’inspire du cadre juridique existant aux Pays-Bas.",
            'source':   "Chambre des représentants de Belgique",
            'date': "02/03/2023",
            'author': ["Vanessa, Matz Les Engagés", "Franky, Demon cd&v"]},
    {'id':   "55K3514",
            'title': "Projet de loi droit de la procédure pénale I."   ,
            'text': "Le projet de loi a pour objet de réformer la procédure pénale sur deux points: d’une part, en ce qui concerne les règles relatives à l’action publique pour des crimes ou délits commis hors du territoire du Royaume et, d’autre part, en ce qui concerne la prescription de l’action publique. Tout d’abord, il restructure et réécrit les articles existants du chapitre II du Titre préliminaire du Code de procédure pénale, en classant dans différentes sections les dispositions relatives à la compétence extraterritoriale des juridictions belges selon les critères traditionnels du droit international public. En outre, le projet de loi vise à réformer le système de prescription. À cet égard, il se fonde sur trois principes de base: 1° des délais suffisamment longs pour mener et clôturer une enquête pénale, sur la base de délais fixes sans possibilité d’interruption de la prescription; 2° la cessation du cours de la prescription dès l’instant où la juridiction de jugement est saisie de l’action publique; 3°  la validité des causes de suspension uniquement lorsqu’il existe réellement un obstacle à l’introduction ou à l’exercice de l’action publique",
            'source':   "Chambre des représentants de Belgique",
            'date': "08/02/2023",
            'author': ["Gouvernement/Regering"]},
    {'id':  "55K3520" ,
            'title': "Projet de loi modifiant la loi du 7 mai 1999 portant création du Palais des Beaux-Arts sous la forme d'une société anonyme de droit public à finalité sociale et modifiant la loi du 30 mars 1995 concernant les réseaux de distribution d'émissions de radiodiffusion et l'exercice d'activités de radiodiffusion dans la région bilingue de Bruxelles-Capitale.",
            'text': "Le Palais des Beaux-Arts (PBA ou BOZAR) est une société anonyme de droit public à finalité sociale. Elle a été créée par une loi du 7 mai 1999 et ses statuts sont contenus dans un arrêté royal du 19 décembre 2001. La finalité sociale est expressément consacrée par l’article 18 de ses statuts (AR 2001). Cette notion n’existe plus dans le nouveau Code des Sociétés et des Associations (CSA) du 23 mars 2019. Il faut donc mettre les dispositions légales et statutaires du PBA en conformité avec le CSA au plus tard pour le 1er janvier 2024 (art. 39 Loi CSA). Il a été décidé, parmi plusieurs possibilités de formes juridiques, de maintenir la forme de SA de droit public, en ne mentionnant plus expressément la finalité sociale mais en maintenant un esprit “non profit”, principalement par l’absence de poursuite de but de lucre. La société restera de droit public, sous le contrôle de l’État fédéral, actionnaire majoritaire, avec un objet inchangé, notamment dans sa mission de service public",
            'source':  "Chambre des représentants de Belgique",
            'date':"02/08/2023",
            'author': ["Gouvernement/Regering"]},
    {'id':  "55K1169" ,
            'title':   "Proposition de loi instaurant une taxe corona de solidarité sur les multimillionnaires." ,
            'text': "Cette proposition de loi établit une taxe unique à charge des multimillionnaires afin de parer aux conséquences sociales de la crise du coronavirus. Son taux d’imposition est de 5 % sur la partie du patrimoine excédant trois millions d’euros ; la première maison d’habitation est exonérée de la taxe, ainsi que les actifs professionnels jusqu’à 500 000 euros chacun au maximum",
            'source':  "Chambre des représentants de Belgique" ,
            'date': "16/04/2020",
            'author': ['Marco, Van Hees PVDA-PTB', "Peter, Mertens PVDA-PTB "]},
    {'id':  "55K2464" ,
            'title':   "Proposition de loi modifiant diverses dispositions en vue de la prescription à l'unité d'antibiotiques, de benzodiazépines et d'opioïdes pour limiter la surconsommation et le surdosage de ces médicaments." ,
            'text': "Certains médicaments sont surconsommés en Belgique. Étant donné que les médecins prescrivent les médicaments et que les pharmaciens les délivrent par boîtes entières, le patient reçoit souvent des quantités inadaptées et excédentaires à l’issue de son traitement. C’est une source d’importants gaspillages de médicaments qui a des conséquences à la fois climatiques et humaines. Outre que les médicaments excédentaires peuvent ensuite polluer l’environnement, il arrive également que certains patients prennent ultérieurement ces médicaments de leur propre initiative, ce qu’il faut éviter. En effet, les personnes qui agissent de la sorte ne suivent pas les instructions d’un médecin et l’usage impropre de médicaments peut être extrêmement nuisible. Des études internationales indiquent que plus de 70 % des ménages conservent des médicaments pour les utiliser ultérieurement. Il convient de promouvoir un usage rationnel des médicaments dans notre société et d’agir pour cela à trois niveaux: en pharmacie, chez le médecin et auprès du citoyen. La stratégie proposée dans cette proposition de loi se concentre sur les deux premiers niveaux en instaurant un nouveau système qui invite les prestataires de soins de santé à toujours prescrire les antibiotiques, les opioïdes et les psychotropes par unité de dosage dans le cadre d’un traitement aigu.",
            'source':  "Chambre des représentants de Belgique" ,
            'date': "27/01/2022",
            'author': ["Nawal, Farih cd&v", "Nahima, Lanjri cd&v"]},
    {'id':  "55K2275" ,
            'title':  "Le démantèlement des centrales nucléaires - Audition du 1er juin 2021 avec les représentants de l'AFCN."  ,
            'text': "Déclassement/démantèlement des installations nucléaires M. Frank Hardeman, directeur général de l’Agence fédérale de Contrôle nucléaire (abréviation: “AFCN”), clarifie ce qu’on entend par déclassement et démantèlement des installations nucléaires (en néerlandais “buitenbedrijfstelling en ontmanteling”, en anglais “decommissioning and dismantling”, souvent abrégé en “D&D” dans le jargon technique). Un site nucléaire doit être déclassé à la fin de sa durée de vie, après quoi il doit être démantelé en toute sécurité afin que le site puisse être libéré et réaffecté pour un nouvel usage. Pour les installations nucléaires, il s’agit d’un processus unique et assez spécifique: il englobe un ensemble d’opérations administratives et techniques pour mettre fin aux activités autorisées sur un site, qui peuvent ou non être soumises à une réglementation. Tant que des matières radioactives sont présentes sur un site, les exigences en matière de radioprotection restent applicables. Les quatre phases suivantes peuvent être distinguées: • la première phase comprend la décision formelle de cesser les activités; • la deuxième phase est la cessation effective; • après quoi, dans une troisième phase, les installations sont démantelées; • dans une quatrième et dernière phase, les sites ou leurs installations sont reclassés conformément à la législation générale. La plupart du temps, en Belgique, les sites ont été libérés, comme cela a été fait après le démantèlement de plusieurs fabriques de combustibles. Si les contrôles réglementaires ne peuvent pas être levés pour toutes les installations d’un site, ils peuvent l’être pour une partie d’entre elles.",
            'source': "Chambre des représentants de Belgique"  ,
            'date': "22/10/2021",
            'author': ["Kurt, Ravyts VB", "Kris, Verduyckt Vooruit"]},
    {'id':  "55K3446" ,
            'title':   "Projet de loi exécutant l'accord cadre dans le cadre des négociations interprofessionnelles pour la période 2023-2024." ,
            'text': "Le 6 avril 2023, les partenaires sociaux, représentés au sein du Groupe des 10, ont conclu un accord dans le cadre des négociations interprofessionnels pour la période 2023-2024. Le Conseil National du Travail a conclu différentes conventions collectives de travail le 30 mai 2023 et a émis l’avis n° 2368 au gouvernement dans lequel elle demande au gouvernement de prendre rapidement et de manière simultanée les textes réglementaires nécessaires afin de donner à l’ensemble des parties prenantes aux niveaux interprofessionnel, sectoriel et d’entreprise, et aux employeurs et travailleurs en général, la sécurité juridique et la garantie de bonne mise en œuvre en vue d’une exécution complète, cohérente entre les différents volets réglementaires et législatifs et répondant ainsi à la demande des partenaires sociaux d’assurer une mise en œuvre du cadre d’accords pour l’ensemble de ses volets, celui-ci formant un tout et étant indivisible. En ce qui concerne les exigences de formes, la section de législation du Conseil d’État observe que l’avant-projet contient des mesures qui, conformément à l’article 15 de la loi du 25 avril 1963 “sur la gestion des organismes d’intérêt public de sécurité sociale et de prévoyance sociale”, doivent être soumises à l’avis du comité de gestion concerné ou du Conseil National du Travail. Une demande d’avis explicite au Conseil national du Travail n’est toutefois pas nécessaire pour ces mesures en l’espèce compte tenu de l’accord du Groupe des 10 et de l’avis très clair rendu par le Conseil national du Travail sur la question (n° 2368).",
            'source': "Chambre des représentants de Belgique"  ,
            'date': "26/06/2023",
            'author': ["Wouter, Vermeersch VB", "Jean-Marc, Delizée PS "]},
    {'id': "55K3360"  ,
            'title':  "Projet de loi modifiant le Code des impôts sur les revenus 1992 en ce qui concerne les indemnités octroyées à des artistes."  ,
            'text': "La loi du 25 avril 2007 modifiant le Code des impôts sur les revenus 1992 en ce qui concerne les indemnités octroyées à des artistes a instauré un régime fiscal pour les activités artistiques qui tombent sous le régime des petites indemnités (article 17sexies de l’arrêté royal du 28 novembre 1969 pris en exécution de la loi du 27 juin 1969 révisant l’arrêté-loi du 28 décembre 1944  concernant la sécurité sociale des travailleurs) sur le plan social. Ce régime fiscal est adapté pour tenir compte des modifications qui sont apportées au régime des petites indemnités, qui devient l’indemnité des arts en amateurs à partir du 1er janvier 2024, sur le plan social. Dans ce contexte, il est fait référence à la loi du 16 décembre 2022 portant création de la Commission du travail des arts et améliorant la protection sociale des travailleurs des arts et l’arrêté royal du 13 mars 2023 relatif au fonctionnement de la Commission du travail des arts, aux critères et à la procédure de reconnaissance des fédérations des arts et à l’amélioration de la protection sociale des travailleurs des arts. Les remarques du Conseil d’État ont été prises en compte. Limitation par année civile Tout comme sur le plan social, la limite de 2.000 euros (montant à indexer, 2.953,27 euros pour l’exercice d’imposition 2024) par année civile (article 38, § 1er, alinéa 1er, 23°, et 97, § 2, du Code des impôts sur les revenus 1992 (CIR 92)) disparaît et fait place à une limitation en fonction du nombre de jours par année civile où des prestations peuvent être fournies pour une indemnité forfaitaire de défraiement exonérée, i.c. 30 jours par année civile. Limitation par jour Pour bénéficier de l’exonération fiscale, un montant maximum par jour par donneur d’ordre s’applique pour les indemnités forfaitaires de défraiement (article 38, § 4, alinéa 2, 2°, CIR 92). Pour l’exercice d’imposition 2024, le montant maximum de l’indemnité forfaitaire de défraiement par jour est de 147,67 euros par donneur d’ordre. Sous le régime modifié, ce montant journalier sera diminué à 70 euros (montant à indexer annuellement – montant de base rattaché à l’indice santé du mois de décembre 2021). Toutefois, en plus de cette indemnité forfaitaire de défraiement, les frais de déplacement réels peuvent désormais être remboursés, limités toutefois à 20 euros par jour (montant à indexer ",
            'source': "Chambre des représentants de Belgique"  ,
            'date': "30/05/2023",
            'author': ["Christian, Leysen Open Vld"]},
    {'id':  "55K3449" ,
            'title':  "Projet de loi modifiant la loi électorale communale, coordonnée le 4 août 1932, en vue de régulariser la situation des citoyens britanniques qui étaient inscrits comme électeurs pour les élections communales avant l'entrée en vigueur du Brexit."  ,
            'text': "La loi électorale communale précise que l’agrément en qualité d’électeur reste valable aussi longtemps que l’intéressé continue à réunir les conditions d’électorat ou n’a pas renoncé à sa qualité d’électeur, quelle que soit la commune de sa résidence en Belgique. Dès lors suite au “Brexit”, les citoyens britanniques perdent une des conditions d’agrément (nationalité d’un État membre de l’Union européenne) et l’agrément en qualité d’électeur n’est plus valable. Les citoyens britanniques, inscrits comme électeurs européens pour les élections communales avant le 31 janvier 2020 et parfois bien impliqués dans la vie de leur commune belge, devraient donc introduire une nouvelle demande de participation au scrutin communal comme citoyen non européen alors qu’une telle démarche a déjà été effectuée dans le passé. Dans un souci d’efficacité administrative, le présent projet de loi introduit une exception à la fin de validité de l’agrément en tant qu’électeur pour les citoyens britanniques.",
            'source':  "Chambre des représentants de Belgique" ,
            'date': "30/06/2023",
            'author': ["Gouvernement/Regering"]},
    {'id':  "55K3422" ,
            'title':   "Projet de loi portant modification de la loi du 13 juin 2005 relative aux communications électroniques et portant réforme des tarifs sociaux." ,
            'text': "Ce projet de loi a pour objet de réformer les tarifs sociaux en matière de communications électroniques, à partir du 1er mars 2024. Il convient de rappeler que la directive (UE) 2018/1972 du Parlement européen et du Conseil du 11 décembre 2018 établissant le code de communications électroniques européen (ci-après de “le Code”) énonce que l’objectif du service universel est de fournir un ensemble de services minimaux aux consommateurs afin de garantir l’inclusion sociale (considérant 212 du Code). Afin de tenir compte des exigences de la directive (UE) 2018/1972 en matière du service universel, le projet de loi s’oriente vers la mise en place d’offres de base qui portent sur l’internet à haut débit fourni en position déterminée. Les caractéristiques minimales de ces offres seront fixées par arrêté royal. Afin de permettre au plus grand nombre de personnes vulnérables de bénéficier du tarif social et, partant, de contribuer à la réduction de la fracture numérique, le projet prévoit des catégories différentes d’ayants droit pour des personnes qui perçoivent ou dont un membre du ménage perçoit certains types d’allocations. Ces catégories sont inspirées de celles qui prévalent en permanence dans le cadre des tarifs sociaux en matière de gaz et d’électricité. Le projet prévoit aussi l’obligation pour les opérateurs offrant aux consommateurs un service d’accès à l’internet à haut débit en position déterminée, qui disposent directement ou indirectement d’un réseau d’accès fixe et qui ont un chiffre d’affaires supérieur à 50 millions d’euros portant sur les services de communications électroniques accessibles au public, de fournir, sur la partie du territoire où ils disposent de leur réseau d’accès, la composante sociale du service universel. Enfin, ce projet de loi prévoit également le maintien du régime actuellement en vigueur pour les ayants droit actuels qui ont introduit leur demande pour bénéficier des tarifs sociaux actuellement en vigueur avant le 1er mars 2024, cela dans le but de permettre à ces bénéficiaires de conserver les avantages acquis sous l’ancien régime",
            'source':  "Chambre des représentants de Belgique" ,
            'date': "13/06/2023",
            'author': ["Gouvernement/Regering"]}]
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    for item in database:
        item["embedding"] = embedder.encode(item["text"], convert_to_tensor=False)
    return database

@st.cache_data
def apply_topic_filter(database, score_threshold):
    search_result = []
    for item in database: 
        cos_score = util.cos_sim(item["embedding"], query_embedding)[0]
        condition = cos_score.abs()
        if condition > score_threshold :
            search_result.append(item)
    return search_result


@st.cache_data
def apply_date_filter(database, start_date, end_date):
    search_result = []
    for item in database: 
        item_date = datetime.datetime.strptime(item['date'], '%d/%m/%Y').date()
        if item_date < start_date or item_date > end_date:
            continue
        else:
            search_result.append(item)
    return search_result

def callback():
    edited_rows = st.session_state["data_editor"]["edited_rows"]
    rows_to_delete = []

    for idx, value in edited_rows.items():
        if value["x"] is True:
            rows_to_delete.append(idx)
    
    #print("df: ", st.session_state["saved_df"])
    #modify the session state 
    st.session_state["modified_df"] = st.session_state["modified_df"].drop(rows_to_delete, axis=0).reset_index(drop=True)
    #df_out = df_out.drop(rows_to_delete, axis=0).reset_index(drop=True)
    
# ---
# Load environment
# ---


database = load_data()

# ---
# Search filter
# ---

#sidebar tryout
# with st.sidebar:
#         st.title("Menu")





#added filter title
st.subheader("Filters")
#columns for layout
col1, col2= st.columns(2)
#first col
with col1:
# Date filter 
    #st.date_input("test date",format="YDD/MM/YYYY")
    start_date = st.date_input('Start date', datetime.date.today() - datetime.timedelta(days=15))
    end_date = st.date_input('End date', datetime.date.today())
    if start_date < end_date:
        st.success('Start date (default: 2 weeks ago): `%s`\n\nEnd date (default: today):`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')

#second col
with col2:
    # Slider to tune the threshold on cos similarity
    score_threshold = st.slider('Filtering threshold: ', 0.0, 0.5, 0.35)
    st.write("Cosine similarity set at", score_threshold)
    st.info('Filter by relevance', icon="ℹ️")
    
# Text field + processing query
embedder = SentenceTransformer('all-MiniLM-L6-v2')
search = st.text_input('Type your search')
query_embedding = embedder.encode(search, convert_to_tensor=False)
    
# Applying the filters


search_result = apply_topic_filter(apply_date_filter(database, start_date, end_date), score_threshold)



try:
    df_temp = pd.DataFrame(search_result)
    df_out = df_temp[['id', 'title', 'author', 'date', 'source', 'text']]


    st.subheader("Search results")
    
    edited_df = st.data_editor(df_out, num_rows="dynamic")
    st.session_state['edited_df']= edited_df


#buffer into session

    buffer = io.BytesIO()
    st.session_state['buffer']=buffer
   
    
    
except KeyError as key:
    print("key error: ", key)
    df_out = pd.DataFrame(search_result)

# ---    
# Outputting an .xlsx file
# ---



