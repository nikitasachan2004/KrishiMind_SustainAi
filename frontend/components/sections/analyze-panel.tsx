'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  ClipboardPaste,
  CloudSun,
  ImagePlus,
  Leaf,
  LoaderCircle,
  MapPinned,
  Sparkles,
  Sprout,
  TrendingUp,
  Upload,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type CropRecommendation = {
  rank: number;
  crop: string;
  composite_score: number;
  predicted_yield_tonnes_per_ha: number;
  predicted_price_inr_per_tonne: number;
  expected_revenue_inr_per_ha: number;
  total_revenue_inr: number;
  risk_level: string;
};

type PlantDiseasePrediction = {
  disease: string;
  confidence: number;
};

type AnalyzeResponse = {
  status: string;
  district: string;
  season: string;
  area_hectares: number;
  scenario_applied: string;
  recommendations: CropRecommendation[];
  plant_disease?: PlantDiseasePrediction | null;
  disclaimer?: string;
  sustainability_disclosure?: string;
};

const seasons = ['Kharif', 'Rabi', 'Summer', 'Autumn', 'Winter', 'Whole Year'];

// No default fallback data - keep form clean until user submits
const fallbackResponse: AnalyzeResponse = {
  status: 'success',
  district: '',
  season: '',
  area_hectares: 0,
  scenario_applied: 'baseline',
  recommendations: [],
  disclaimer: '',
  sustainability_disclosure: '',
};

export function AnalyzePanel() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [district, setDistrict] = useState('Guntur');
  const [season, setSeason] = useState('Kharif');
  const [area, setArea] = useState('10');
  const [rainfallDelta, setRainfallDelta] = useState('0');
  const [tempDelta, setTempDelta] = useState('0');

  const recommendations = response?.recommendations ?? [];
  const topCrop = recommendations[0];
  const disease = response?.plant_disease ?? null;
  const usingFallback = !response;

  const diseaseMatches = useMemo(() => {
    if (!disease) {
      return [];
    }

    const first = {
      label: disease.disease,
      confidence: disease.confidence,
    };

    return [
      first,
      {
        label: topCrop?.crop ? `${topCrop.crop} suitability signal` : 'Fallback agronomy signal',
        confidence: Math.max(first.confidence * 0.72, 0.18),
      },
      {
        label: 'Further field inspection',
        confidence: Math.max(1 - first.confidence, 0.12),
      },
    ];
  }, [disease, topCrop]);

  const averageScore = useMemo(() => {
    if (!recommendations.length) {
      return 0;
    }

    return (
      recommendations.reduce((total, item) => total + item.composite_score, 0) /
      recommendations.length
    );
  }, [recommendations]);

  const extractImageFile = (files: FileList | File[] | null | undefined) => {
    if (!files) {
      return null;
    }

    return Array.from(files).find((candidate) => candidate.type.startsWith('image/')) ?? null;
  };

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    setError(null);
  };

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  const handlePaste = async () => {
    try {
      const clipboardItems = await navigator.clipboard.read();
      for (const item of clipboardItems) {
        const imageType = item.types.find((type) => type.startsWith('image/'));
        if (imageType) {
          const blob = await item.getType(imageType);
          const pastedFile = new File([blob], 'krishimind-leaf.png', { type: imageType });
          handleFileChange(pastedFile);
          return;
        }
      }
      setError('Clipboard does not contain an image yet.');
    } catch {
      setError('Clipboard image paste needs browser permission. You can also drag and drop a file.');
    }
  };

  useEffect(() => {
    const onPaste = (event: ClipboardEvent) => {
      const pastedImage = extractImageFile(event.clipboardData?.files);
      if (pastedImage) {
        event.preventDefault();
        handleFileChange(pastedImage);
      }
    };

    window.addEventListener('paste', onPaste);
    return () => window.removeEventListener('paste', onPaste);
  }, []);

  const onDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setDragActive(false);
    const droppedImage = extractImageFile(event.dataTransfer.files);
    if (droppedImage) {
      handleFileChange(droppedImage);
    } else {
      setError('Please drop an image file.');
    }
  };

  const handleAnalyze = async () => {
    if (!district.trim()) {
      setError('Please enter a district before running the analysis.');
      return;
    }

    if (!area || Number(area) <= 0) {
      setError('Area must be greater than zero.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('district', district.trim());
      formData.append('season', season);
      formData.append('area', area);
      formData.append('rainfall_delta', rainfallDelta);
      formData.append('temp_delta', tempDelta);

      if (file) {
        formData.append('file', file);
      }

      const routeResponse = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      const payload = (await routeResponse.json()) as AnalyzeResponse & { error?: string };

      if (!routeResponse.ok) {
        setError(
          payload.error ??
            'Analysis failed. Please check your inputs and try again.'
        );
        return;
      }

      setResponse(payload);
    } catch {
      setError(
        'The analysis service is not responding. Please try again later.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-8 xl:grid-cols-[1.06fr_0.94fr]">
      <div className="space-y-8">
        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-lg font-semibold">Field Inputs</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Blend crop planning with optional disease detection in one run.
              </p>
            </div>
            <div className="rounded-full bg-primary/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
              KrishiMind Combined Analysis
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium">District</span>
              <input
                value={district}
                onChange={(event) => setDistrict(event.target.value)}
                className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                placeholder="Guntur"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium">Season</span>
              <select
                value={season}
                onChange={(event) => setSeason(event.target.value)}
                className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              >
                {seasons.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium">Area (hectares)</span>
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={area}
                onChange={(event) => setArea(event.target.value)}
                className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium">Rainfall delta</span>
              <div className="rounded-2xl border border-border bg-background/80 px-4 py-3">
                <input
                  type="range"
                  min="-1"
                  max="1"
                  step="0.05"
                  value={rainfallDelta}
                  onChange={(event) => setRainfallDelta(event.target.value)}
                  className="w-full accent-lime-700"
                />
                <p className="mt-2 text-sm text-muted-foreground">
                  {(Number(rainfallDelta) * 100).toFixed(0)}%
                </p>
              </div>
            </label>

            <label className="space-y-2 md:col-span-2">
              <span className="text-sm font-medium">Temperature delta</span>
              <div className="rounded-2xl border border-border bg-background/80 px-4 py-3">
                <input
                  type="range"
                  min="-5"
                  max="10"
                  step="0.5"
                  value={tempDelta}
                  onChange={(event) => setTempDelta(event.target.value)}
                  className="w-full accent-emerald-700"
                />
                <p className="mt-2 text-sm text-muted-foreground">{Number(tempDelta).toFixed(1)}°C</p>
              </div>
            </label>
          </div>
        </div>

        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <Upload className="size-5" />
            </div>
            <div>
              <p className="text-lg font-semibold">Leaf Image</p>
              <p className="text-sm text-muted-foreground">
                Optional. Add a leaf photo to receive disease detection alongside crop recommendations.
              </p>
            </div>
          </div>

          <label
            className={cn(
              'mt-6 flex min-h-80 cursor-pointer flex-col items-center justify-center rounded-[1.5rem] border border-dashed border-primary/30 bg-gradient-to-br from-lime-50 to-emerald-50 p-6 text-center transition hover:border-primary/50 dark:from-slate-900 dark:to-emerald-950/60',
              dragActive && 'scale-[1.01] border-primary bg-primary/5'
            )}
            onDragEnter={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragActive(false);
            }}
            onDrop={onDrop}
          >
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Leaf preview"
                className="h-full max-h-72 w-full rounded-[1.25rem] object-cover"
              />
            ) : (
              <>
                <ImagePlus className="size-10 text-primary" />
                <p className="mt-4 text-lg font-medium">Drag and drop, paste, or click to browse</p>
                <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                  Capture the full leaf under natural light for a cleaner disease classification signal.
                </p>
              </>
            )}
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)}
            />
          </label>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button onClick={handleAnalyze} size="lg" className="rounded-full px-6">
              {loading ? (
                <LoaderCircle className="mr-2 size-4 animate-spin" />
              ) : (
                <Sparkles className="mr-2 size-4" />
              )}
              Run KrishiMind Analysis
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              className="rounded-full px-6"
              onClick={handlePaste}
            >
              <ClipboardPaste className="mr-2 size-4" />
              Paste Image
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              className="rounded-full px-6"
              onClick={() => handleFileChange(null)}
            >
              Reset Image
            </Button>
          </div>

          {error ? (
            <div className="mt-4 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200">
              <AlertCircle className="mt-0.5 size-4 shrink-0" />
              <p>{error}</p>
            </div>
          ) : null}
        </div>
      </div>

      <div className="space-y-6">
        <div className="rounded-[2rem] border border-border/60 bg-slate-950 p-6 text-white shadow-xl">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-lime-300/70">Plant health</p>
              <p className="mt-4 text-3xl font-semibold">
                {disease?.disease ?? 'Awaiting optional image'}
              </p>
              <p className="mt-3 text-sm text-slate-300">
                {disease
                  ? `Confidence score: ${(disease.confidence * 100).toFixed(2)}%`
                  : 'Upload a leaf image to add disease classification to your planning run.'}
              </p>
            </div>
            <div className="rounded-[1.5rem] bg-white/5 p-4 text-right">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p className="mt-2 text-sm font-medium">
                {usingFallback ? 'Sample preview' : 'Live backend response'}
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            {diseaseMatches.map((item) => (
              <div key={item.label} className="rounded-[1.25rem] border border-white/10 bg-white/5 p-4">
                <p className="text-sm text-slate-300">{item.label}</p>
                <p className="mt-3 text-2xl font-semibold">
                  {(item.confidence * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <MetricCard
            icon={MapPinned}
            label="District"
            value={response?.district ?? fallbackResponse.district}
            helper={response?.season ?? fallbackResponse.season}
          />
          <MetricCard
            icon={Sprout}
            label="Top crop"
            value={topCrop?.crop ?? 'Awaiting run'}
            helper={topCrop ? `${topCrop.risk_level} risk` : 'No recommendation yet'}
          />
          <MetricCard
            icon={TrendingUp}
            label="Average score"
            value={averageScore.toFixed(3)}
            helper="Higher is better"
          />
          <MetricCard
            icon={CloudSun}
            label="Area"
            value={`${response?.area_hectares ?? fallbackResponse.area_hectares} ha`}
            helper={`Scenario: ${response?.scenario_applied ?? fallbackResponse.scenario_applied}`}
          />
        </div>

        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex items-center justify-between">
            <p className="text-lg font-semibold">Crop recommendations</p>
            <p className="text-sm text-muted-foreground">District-level optimization</p>
          </div>
          <div className="mt-6 space-y-4">
            {recommendations.map((item) => (
              <div key={`${item.rank}-${item.crop}`} className="rounded-[1.5rem] border border-border/60 bg-background/70 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-muted-foreground">Rank #{item.rank}</p>
                    <p className="text-xl font-semibold">{item.crop}</p>
                  </div>
                  <div className="rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
                    Score {item.composite_score.toFixed(3)}
                  </div>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <MiniStat label="Yield" value={`${item.predicted_yield_tonnes_per_ha.toFixed(2)} t/ha`} />
                  <MiniStat label="Revenue / ha" value={`₹${Math.round(item.expected_revenue_inr_per_ha).toLocaleString()}`} />
                  <MiniStat label="Risk" value={item.risk_level} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-border/60 bg-white/80 p-6 text-sm leading-6 text-muted-foreground shadow-xl shadow-lime-900/5">
          <p>{response?.disclaimer ?? fallbackResponse.disclaimer}</p>
          <p className="mt-3">
            {response?.sustainability_disclosure ?? fallbackResponse.sustainability_disclosure}
          </p>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  helper,
}: {
  icon: typeof MapPinned;
  label: string;
  value: string;
  helper: string;
}) {
  return (
    <div className="rounded-[1.75rem] border border-border/60 bg-card/90 p-5 shadow-lg shadow-lime-900/5">
      <Icon className="size-5 text-primary" />
      <p className="mt-4 text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="mt-2 text-sm text-muted-foreground">{helper}</p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[1rem] bg-secondary/60 p-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-sm font-semibold">{value}</p>
    </div>
  );
}
