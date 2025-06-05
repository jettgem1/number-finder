# PDF Number Finder

A web application that analyzes PDF files to find the largest numbers within them, both raw and after unit adjustments.

## Features

- Upload PDF files through a modern web interface
- Find the largest raw number in the PDF
- Find the largest number after unit adjustments (e.g., converting units like million, billion)
- Clean, responsive UI with drag-and-drop support

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- Python (for PDF analysis)

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. Visit the homepage and click "Try PDF Number Finder"
2. Upload a PDF file by dragging and dropping or clicking the upload area
3. Click "Find Numbers" to analyze the PDF
4. View the results showing both the largest raw number and the largest adjusted number

## Development

The application consists of:
- Frontend: Next.js pages in the `app` directory
- PDF Analysis: Python scripts in the root directory
- API: Next.js API routes in `app/api`

## License

MIT
