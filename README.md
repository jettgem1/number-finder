# PDF Number Finder

A web application that analyzes PDF files to find the largest numbers within them, both raw numbers and numbers with unit adjustments (e.g., "5 million" = 5,000,000).

## Features

- Modern web interface for PDF upload
- Drag-and-drop file upload
- Finds two types of numbers:
  - Largest raw number (e.g., "1000")
  - Largest adjusted number (e.g., "1 million" = 1,000,000)
- Real-time processing
- Responsive design

## Tech Stack

- Frontend: Next.js 13+ with App Router
- Backend: Next.js API Routes
- PDF Processing: Python with pdfminer.six
- Styling: Tailwind CSS

## Local Development

1. Install dependencies:
```bash
npm install
pip install -r requirements.txt
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## How It Works

1. User uploads a PDF file through the web interface
2. The file is sent to a Next.js API route
3. The API route:
   - Saves the PDF temporarily
   - Spawns a Python process to analyze the PDF
   - Extracts text from all pages
   - Finds the largest numbers (both raw and adjusted)
4. Results are displayed to the user

## Deployment

The application is configured for deployment on Vercel. The `vercel.json` file includes necessary configurations for:
- Next.js build settings
- Node.js runtime for API routes
- Python dependency handling

## Project Structure

```
├── app/
│   ├── api/
│   │   └── analyze-pdf/
│   │       └── route.ts    # API endpoint for PDF analysis
│   ├── pdf-finder/
│   │   └── page.tsx        # PDF upload interface
│   └── page.tsx            # Home page
├── utils/
│   ├── pdf_text_extractor.py
│   └── number_parser.py
├── main.py                 # Python PDF analysis script
├── requirements.txt        # Python dependencies
└── package.json           # Node.js dependencies
```
