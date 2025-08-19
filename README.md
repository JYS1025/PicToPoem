# 📸 PicToPoem - Poetry from a Picture

## 🎯 About the Project

**PicToPoem** is an AI-powered web application that analyzes your uploaded images and recommends a fitting passage from a literary work. It utilizes the Google Gemini AI to analyze the mood and sentiment of the image, then finds the most suitable quote from real literary works, providing it with a curator's commentary.

### ✨ Key Features

- **Image Analysis**: The AI analyzes the mood, color palette, and emotional tone of the uploaded image.
- **Literary Recommendations**: Recommends passages from real literary works that match the image.
- **Curator's Commentary**: Provides professional commentary on why the specific work was chosen.
- **Story Image Generation**: Creates an Instagram Story-style image with the recommended literary passage.
- **Responsive Design**: Conveniently usable on both mobile and desktop.

## 🏗️ Tech Stack

### Backend
- **Flask**: Python web framework
- **Google Gemini AI**: For image analysis and text generation
- **Pillow (PIL)**: For image processing
- **python-dotenv**: For managing environment variables

### Frontend
- **HTML5**: For the structure of the web page
- **CSS3**: For styling and responsive design
- **JavaScript (ES6+)**: For client-side interactions

## 📋 Installation and Setup

### 1. Prerequisites

- Python 3.8 or higher
- A Google Gemini AI API Key

### 2. Clone the Project

```bash
git clone <repository-url>
cd PicToPoem
```

### 3. Create and Activate a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the project's root directory and add the following content:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**How to get a Google Gemini AI API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey).
2. Log in with your Google account.
3. Click "Create API Key".
4. Copy the generated API key and paste it into the `.env` file.

### 6. Prepare Font Files

Add a Korean font file to the `backend` directory:
- **Required Font File:** `Gyeong-gi_Regular.ttf`
- You can use any other `.ttf` font, but you will need to modify the `app.py` source code.

### 7. Run the Application

```bash
# Navigate to the backend directory
cd backend

# Run the Flask server
python app.py
```

### 8. Access in a Web Browser

Open your browser and go to the following address:
```
http://localhost:5000
```

## 🚀 How to Use

### 1. Upload an Image
- Click the "Select Image" button to choose an image for analysis.
- Supported formats: Common image formats like JPG, PNG, GIF, etc.

### 2. Generate a Quote
- After selecting an image, click the "Generate Quote" button.
- Wait a moment while the AI analyzes the image to find a suitable literary work.

### 3. View the Result
- See the recommended literary quote.
- Check the author and title of the work.
- Read the curator's commentary.

### 4. Save the Story Image
- Click the "Save as Story Image" button to download an Instagram Story-style image.
- The generated image will be automatically saved to your download folder.

## 📁 Project Structure

```
PicToPoem/
├── backend/                 # Backend server
│   ├── app.py             # Main Flask application file
│   └── Gyeong-gi_Regular.ttf # Korean font file
├── frontend/               # Frontend files
│   ├── index.html         # Main HTML page
│   ├── style.css          # CSS stylesheet
│   └── script.js          # JavaScript for interactions
├── venv/                  # Python virtual environment (auto-generated)
├── requirements.txt        # Python dependency list
├── .env                   # Environment variables file (user-created)
├── .gitignore            # Git ignore file list
└── README.md             # Project documentation
```

## 🔧 API Endpoints

### POST `/api/generate`
Analyzes an image and recommends a literary work.

**Request:**
- `Content-Type: multipart/form-data`
- Body: `image` (image file)

**Response:**
```json
{
  "quote": "The recommended literary quote",
  "source": {
    "title": "Title of the work",
    "author": "Author's name"
  },
  "commentary": "The curator's commentary"
}
```

### POST `/api/create-story`
Generates a story image.

**Request:**
- `Content-Type: multipart/form-data`
- Body: 
  - `image` (original image file)
  - `quote` (the quote)
  - `author` (the author's name)
  - `title` (the title of the work)

**Response:**
- `Content-Type: image/png`
- Body: The generated story image file

## 🔒 Security Notice

- Store your API key in the `.env` file (never hardcode it in the source).
- The `.env` file is included in `.gitignore` and will not be uploaded to Git.
- Keep your API key safe and do not expose it publicly.

## 🐛 Troubleshooting

### Common Errors

1. **"GEMINI_API_KEY is not set"**
   - Make sure the `.env` file is in the correct location.
   - Verify that the API key is entered correctly.

2. **"No image file"**
   - Ensure the image file is in a supported format.
   - Check that the file size is not too large.

3. **"Invalid AI response format"**
   - Check your internet connection.
   - Verify that your API key is valid.

### Checking Logs
Error messages will be printed to the console where the Flask server is running. Refer to these logs for troubleshooting.

## 📄 License

This project is distributed under the MIT License.

## 🤝 Contributing

1. Fork this repository.
2. Create a new feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Create a Pull Request.

## 📞 Contact

If you have any questions about the project, please create an issue.

---

Discover beautiful literary works that match your photos with **PicToPoem**! 📖✨