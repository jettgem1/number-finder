import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('pdf') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Create a temporary file
    const bytes = await file.arrayBuffer();
    const buffer = new Uint8Array(bytes);
    const tempFilePath = join(tmpdir(), `upload-${Date.now()}.pdf`);
    await writeFile(tempFilePath, buffer);

    // Run the Python script
    const result = await new Promise<string>((resolve, reject) => {
      const pythonProcess = spawn('python', ['main.py', tempFilePath]);
      let output = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}: ${error}`));
          return;
        }
        resolve(output);
      });
    });

    // Parse the output
    const lines = result.toString().split('\n');
    const rawMax = lines.find(line => line.includes('Largest raw number found:'))?.split(':')[1]?.trim() || '0';
    const adjustedMax = lines.find(line => line.includes('Largest number after unit adjustments:'))?.split(':')[1]?.trim() || '0';

    return NextResponse.json({
      rawMax,
      adjustedMax
    });

  } catch (error) {
    console.error('Error processing PDF:', error);
    return NextResponse.json(
      { error: 'Failed to process PDF' },
      { status: 500 }
    );
  }
} 