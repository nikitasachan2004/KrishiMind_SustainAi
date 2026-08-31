import { randomUUID } from 'crypto';
import { promises as fs } from 'fs';
import os from 'os';
import path from 'path';

import { NextRequest, NextResponse } from 'next/server';

const rawBackendUrl =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  'http://127.0.0.1:8000';

const BACKEND_URL = rawBackendUrl.replace(/\/$/, '');

export async function POST(request: NextRequest) {
  let tempFilePath: string | null = null;

  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const district = String(formData.get('district') ?? 'Guntur').trim() || 'Guntur';
    const season = String(formData.get('season') ?? 'Kharif').trim() || 'Kharif';
    const area = Number(formData.get('area') ?? '10');
    const rainfallDelta = Number(formData.get('rainfall_delta') ?? '0');
    const tempDelta = Number(formData.get('temp_delta') ?? '0');

    const payload: Record<string, unknown> = {
      district,
      season,
      area: Number.isFinite(area) && area > 0 ? area : 10,
      scenario: {
        rainfall_delta: Number.isFinite(rainfallDelta) ? rainfallDelta : 0,
        temp_delta: Number.isFinite(tempDelta) ? tempDelta : 0,
      },
    };

    if (file instanceof File && file.size > 0) {
      const bytes = Buffer.from(await file.arrayBuffer());
      const extension = path.extname(file.name) || '.png';
      tempFilePath = path.join(os.tmpdir(), `${randomUUID()}${extension}`);
      await fs.writeFile(tempFilePath, bytes);
      payload.image_path = tempFilePath;
    }

    const response = await fetch(`${BACKEND_URL}/predict/crop-plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      cache: 'no-store',
    });

    const backendPayload = await response.json().catch(() => null);

    if (!response.ok) {
      return NextResponse.json(
        {
          error:
            backendPayload?.detail?.message ??
            backendPayload?.detail ??
            backendPayload?.error ??
            `Backend prediction failed with status ${response.status}.`,
        },
        { status: response.status }
      );
    }

    return NextResponse.json(backendPayload, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Could not connect to the KrishiMind backend service.',
      },
      { status: 503 }
    );
  } finally {
    if (tempFilePath) {
      await fs.unlink(tempFilePath).catch(() => undefined);
    }
  }
}
