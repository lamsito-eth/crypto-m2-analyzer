# 📊 Crypto vs M2 Liquidity Analyzer

**Une web app pour analyser la corrélation entre le Total Crypto Market Cap et la liquidité M2 globale, avec analyse du lag temporel.**

![Dashboard](https://img.shields.io/badge/Status-Production-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)

## 🎯 Qu'est-ce que c'est ?

Cet outil montre que **la liquidité M2 (money supply) LEAD les mouvements du marché crypto de plusieurs semaines**.

Quand la liquidité globale augmente → le crypto pump quelques semaines après ! 🚀

## ✨ Features

- ✅ **Fetch automatique des données** (CoinGecko + FRED API)
- ✅ **Upload de CSV personnalisés** (TradingView exports)
- ✅ **Analyse de lag automatique** (trouve le délai optimal)
- ✅ **Calcul du M2 Z-Score** (méthode TradingView)
- ✅ **Charts interactifs** style dark professionnel
- ✅ **Export des résultats** en CSV
- ✅ **100% gratuit** et open source

## 🚀 Déploiement sur Streamlit Cloud (GRATUIT)

### Étape 1 : Créer un compte GitHub
1. Va sur [github.com](https://github.com) et crée un compte (gratuit)
2. Crée un nouveau repository (appelé `crypto-m2-analyzer` par exemple)

### Étape 2 : Upload les fichiers
Upload ces 3 fichiers dans ton repo :
- `app.py` (l'application)
- `requirements.txt` (les dépendances)
- `README.md` (cette doc)

### Étape 3 : Déployer sur Streamlit Cloud
1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Connecte ton compte GitHub
3. Clique sur "New app"
4. Sélectionne ton repository `crypto-m2-analyzer`
5. Main file path : `app.py`
6. Clique sur "Deploy" !

**🎉 En 2 minutes, ton app est en ligne avec un lien public !**

Exemple de lien : `https://your-app.streamlit.app`

## 💻 Lancer localement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

L'app s'ouvre sur `http://localhost:8501`

## 📖 Comment utiliser ?

### Option 1 : Auto-fetch (Recommandé)
1. Sélectionne "Fetch from APIs (Auto)"
2. Clique sur "🚀 Run Analysis"
3. L'app récupère automatiquement les données de CoinGecko et FRED
4. Boom ! Tu as ton dashboard avec l'analyse du lag

### Option 2 : Upload CSV
1. Sélectionne "Upload CSV Files"
2. Upload ton export TradingView du Total Crypto Market Cap
3. Upload ton export du M2 Liquidity
4. Clique sur "🚀 Run Analysis"

**Format CSV attendu :**
```
Date,Value
2020-01-01,1000000000
2020-01-02,1050000000
...
```

## 🎨 Screenshots

### Dashboard principal
[La chart avec crypto (blanc) et M2 Z-Score (barres vertes/rouges)]

### Analyse de corrélation
[Graph montrant comment la corrélation varie selon le lag]

## 🔧 Personnalisation

Tu peux ajuster dans la sidebar :
- **Max Lag Analysis** : Jusqu'à combien de semaines analyser (défaut : 20)
- **Z-Score Window** : Fenêtre pour calculer le Z-Score (défaut : 90 jours)

## 📊 Sources de données

- **Crypto Market Cap** : CoinGecko API (gratuit)
- **M2 Money Supply** : FRED (Federal Reserve Economic Data)
- **Calcul Z-Score** : Méthode identique à TradingView

## 🤝 Partage

Une fois déployé sur Streamlit Cloud, partage ton lien avec :
- Tes potes traders
- Twitter crypto
- Discord/Telegram
- Reddit (r/CryptoCurrency)

Tout le monde peut l'utiliser gratuitement sans rien installer !

## 💡 Insights clés

**📈 Pattern typique :**
1. La Fed/BCE augmente M2 (QE, stimulus)
2. Le Z-Score devient positif (barres vertes)
3. 4-8 semaines plus tard → crypto pump
4. La corrélation est souvent entre 0.5-0.8 au lag optimal

**📉 Pendant les bear markets :**
- M2 se contracte (QT)
- Z-Score négatif (barres rouges)
- Crypto dump avec quelques semaines de retard

## 🛠️ Tech Stack

- **Frontend** : Streamlit (Python)
- **Data** : Pandas, NumPy
- **Charts** : Matplotlib
- **APIs** : CoinGecko, FRED
- **Hosting** : Streamlit Cloud (gratuit)

## 📝 Prochaines features (idées)

- [ ] Support de plus d'indicateurs (DXY, BTC Dominance)
- [ ] Alertes email quand M2 change
- [ ] Backtesting de stratégies basées sur M2
- [ ] Export PDF du rapport
- [ ] Mode "dark/light" toggle

## 🐛 Bugs ou questions ?

Ouvre une issue sur GitHub ou DM sur Twitter !

## 📜 License

MIT - Fais-en ce que tu veux !

---

**Made with ❤️ by [Ton Nom]**

*Si ça t'aide à pump tes bags, partage le tool ! 🚀*
