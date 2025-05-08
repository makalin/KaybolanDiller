# 🌍 KaybolanDiller

**KaybolanDiller** (Lost Languages) is an open-source AI-powered translator for rare and endangered languages, with a special focus on Turkish and Turkic dialects. Inspired by tools like Google Translate, this project aims to preserve linguistic heritage through modern deep learning techniques.

---

## ✨ Features

- 🔤 Translate between rare and high-resource languages (e.g., Ainu ↔ English, Meskhetian ↔ Turkish)
- 🤖 Built using Hugging Face Transformers and transfer learning
- 🌐 Language selector supporting global and Turkic language families
- 🧠 Fine-tuned models for endangered dialects
- 📂 Open dataset and model repository
- 🚀 Deployable via GitHub + Hugging Face + Vercel

---

## 🧠 Supported Language Families

- **Turkish Dialects**: Meskhetian, Karamanlı, Gagauz, Rumelian, Cypriot
- **Turkic Languages**: Uyghur, Chuvash, Kazakh, Bashkir, Crimean Tatar, etc.
- **Other Rare Languages**: Ainu, Cherokee, Basque (with aligned datasets)

See the full list of supported languages and dialects in [languages.md](./languages.md).

---

## 🛠 Tech Stack

| Layer         | Tools                                      |
|---------------|---------------------------------------------|
| Frontend      | SvelteKit / Vue 3, Animora (custom CSS)     |
| Backend       | FastAPI (Python)                            |
| AI Models     | PyTorch + Hugging Face Transformers         |
| Data          | OPUS, ELAR, Wikimedia Incubator             |
| Deployment    | Vercel (frontend) + Hugging Face Spaces     |

---

## 🚧 Project Structure

```

KaybolanDiller/
├── datasets/              # Rare language pair corpora
├── models/                # Pretrained and fine-tuned models
├── api/                   # FastAPI endpoints
├── webapp/                # SvelteKit frontend (dark theme)
├── notebooks/             # Jupyter notebooks for training
├── requirements.txt
└── README.md

```

---

## 🌐 Demo (Coming Soon)

Stay tuned for a live web demo!  
We aim to host the translator with open APIs and interactive UI.

---

## 🤝 Contributing

We welcome contributors passionate about language preservation, NLP, and open-source AI.  
Check out the [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## 📜 License

[MIT License](LICENSE)

---

## 📣 Credits

Project by [Mehmet T. AKALIN](https://github.com/makalin)  
Powered by Hugging Face, PyTorch, and the global linguist community.
