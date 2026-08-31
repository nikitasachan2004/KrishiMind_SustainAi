'use client';

import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  CloudRain,
  CloudSun,
  Coins,
  Droplet,
  Flame,
  Info,
  Layers,
  Leaf,
  LoaderCircle,
  MapPinned,
  ShieldCheck,
  Sparkles,
  Sprout,
  Thermometer,
  TrendingUp,
  Wind,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type SustainabilityMetrics = {
  water_use_estimate: number;
  water_saved_vs_baseline: number;
  fertilizer_proxy: number;
  carbon_proxy: number;
  risk_reduction_pct: number;
  sustainability_score: number;
};

type CropRecommendation = {
  rank: number;
  crop: string;
  composite_score: number;
  predicted_yield_tonnes_per_ha: number;
  predicted_price_inr_per_tonne: number;
  expected_revenue_inr_per_ha: number;
  total_revenue_inr: number;
  risk_level: string;
  sustainability_metrics?: SustainabilityMetrics | null;
  proxy_metrics?: boolean;
};

type AnalyzeResponse = {
  status: string;
  district: string;
  season: string;
  area_hectares: number;
  scenario_applied: string;
  recommendations: CropRecommendation[];
  disclaimer?: string;
  sustainability_disclosure?: string;
};

const seasons = ['Kharif', 'Rabi', 'Summer', 'Autumn', 'Winter', 'Whole Year'];

const popularDistricts = [
  { name: 'Guntur', state: 'AP', defaultSeason: 'Kharif' },
  { name: 'Nagpur', state: 'MH', defaultSeason: 'Kharif' },
  { name: 'Patna', state: 'BR', defaultSeason: 'Rabi' },
  { name: 'Ludhiana', state: 'PB', defaultSeason: 'Rabi' },
  { name: 'Coimbatore', state: 'TN', defaultSeason: 'Whole Year' },
  { name: 'Bhopal', state: 'MP', defaultSeason: 'Kharif' },
];

const climatePresets = [
  { label: 'Normal Baseline', rainfall: '0', temp: '0', icon: CloudSun },
  { label: 'Mild Drought (-10%)', rainfall: '-0.1', temp: '0.5', icon: CloudRain },
  { label: 'Severe Drought (-30%)', rainfall: '-0.3', temp: '1.5', icon: Flame },
  { label: 'Moderate Warming (+2°C)', rainfall: '0', temp: '2.0', icon: Thermometer },
  { label: 'Combined Stress (-20%, +2°C)', rainfall: '-0.2', temp: '2.0', icon: Wind },
];

export function AnalyzePanel() {
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [district, setDistrict] = useState('Guntur');
  const [season, setSeason] = useState('Kharif');
  const [area, setArea] = useState('10');
  const [rainfallDelta, setRainfallDelta] = useState('0');
  const [tempDelta, setTempDelta] = useState('0');
  const [activeTab, setActiveTab] = useState<'advisory' | 'sustainability' | 'economics'>('advisory');

  const recommendations = response?.recommendations ?? [];
  const topCrop = recommendations[0];

  const averageScore = useMemo(() => {
    if (!recommendations.length) return 0;
    return (
      recommendations.reduce((total, item) => total + item.composite_score, 0) /
      recommendations.length
    );
  }, [recommendations]);

  const maxRevenue = useMemo(() => {
    if (!recommendations.length) return 1;
    return Math.max(...recommendations.map((r) => r.total_revenue_inr));
  }, [recommendations]);

  const handleAnalyze = async () => {
    if (!district.trim()) {
      setError('Please enter a valid district name.');
      return;
    }

    if (!area || Number(area) <= 0) {
      setError('Farm area must be greater than zero hectares.');
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

      const routeResponse = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      const payload = (await routeResponse.json()) as AnalyzeResponse & { error?: string };

      if (!routeResponse.ok) {
        setError(
          payload.error ?? 'Analysis failed. Please verify the district name and try again.'
        );
        return;
      }

      setResponse(payload);
    } catch {
      setError('The KrishiMind backend service is not responding. Please check server status.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
      {/* Left Column: Input Form & Simulation Controls */}
      <div className="space-y-8">
        {/* Farm & District Card */}
        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="flex size-2 rounded-full bg-emerald-500 animate-pulse" />
                <p className="text-xl font-bold tracking-tight text-foreground">Farm & Regional Context</p>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Configured for 706 Indian districts with ICRISAT & AGMARKNET models.
              </p>
            </div>
            <span className="rounded-full border border-primary/20 bg-primary/10 px-3.5 py-1 text-xs font-semibold text-primary">
              ML Precision Engine
            </span>
          </div>

          {/* Quick District Chips */}
          <div className="mt-5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Quick District Presets
            </span>
            <div className="mt-2 flex flex-wrap gap-2">
              {popularDistricts.map((item) => (
                <button
                  key={item.name}
                  type="button"
                  onClick={() => {
                    setDistrict(item.name);
                    setSeason(item.defaultSeason);
                  }}
                  className={cn(
                    'rounded-full border px-3 py-1 text-xs font-medium transition',
                    district.toLowerCase() === item.name.toLowerCase()
                      ? 'border-primary bg-primary/15 font-semibold text-primary'
                      : 'border-border/60 bg-secondary/40 text-muted-foreground hover:border-primary/40 hover:text-foreground'
                  )}
                >
                  {item.name} ({item.state})
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                District Name
              </span>
              <div className="relative">
                <input
                  value={district}
                  onChange={(event) => setDistrict(event.target.value)}
                  className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 pl-10 text-sm font-medium outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="e.g. Guntur, Nagpur, Patna"
                />
                <MapPinned className="pointer-events-none absolute left-3.5 top-3.5 size-4 text-muted-foreground" />
              </div>
            </label>

            <label className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Growing Season
              </span>
              <select
                value={season}
                onChange={(event) => setSeason(event.target.value)}
                className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 text-sm font-medium outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              >
                {seasons.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 sm:col-span-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Cultivable Plot Area (Hectares)
              </span>
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={area}
                onChange={(event) => setArea(event.target.value)}
                className="w-full rounded-2xl border border-border bg-background/80 px-4 py-3 text-sm font-medium outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </label>
          </div>
        </div>

        {/* Climate Scenario Simulation Card */}
        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xl font-bold tracking-tight text-foreground">Climate What-If Simulation</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Stress-test crop resilience against precipitation anomalies and heatwaves.
              </p>
            </div>
            <div className="rounded-full bg-emerald-500/10 p-2.5 text-emerald-600 dark:text-emerald-400">
              <CloudSun className="size-5" />
            </div>
          </div>

          {/* Presets */}
          <div className="mt-4">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Climate Stress Scenarios
            </span>
            <div className="mt-2 flex flex-wrap gap-2">
              {climatePresets.map((preset) => {
                const isSelected = rainfallDelta === preset.rainfall && tempDelta === preset.temp;
                const Icon = preset.icon;
                return (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => {
                      setRainfallDelta(preset.rainfall);
                      setTempDelta(preset.temp);
                    }}
                    className={cn(
                      'flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-xs font-medium transition',
                      isSelected
                        ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                        : 'border-border/70 bg-secondary/50 text-muted-foreground hover:border-primary/40 hover:text-foreground'
                    )}
                  >
                    <Icon className="size-3.5" />
                    {preset.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sliders */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="space-y-2 rounded-2xl border border-border bg-background/80 p-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Rainfall Delta
                </span>
                <span className="text-sm font-bold text-foreground">
                  {(Number(rainfallDelta) * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="-1"
                max="1"
                step="0.05"
                value={rainfallDelta}
                onChange={(event) => setRainfallDelta(event.target.value)}
                className="w-full accent-primary"
              />
              <p className="text-[11px] text-muted-foreground">
                {Number(rainfallDelta) < 0
                  ? 'Simulating monsoon drought'
                  : Number(rainfallDelta) > 0
                  ? 'Simulating surplus precipitation'
                  : 'Normal historical rainfall'}
              </p>
            </div>

            <div className="space-y-2 rounded-2xl border border-border bg-background/80 p-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Temperature Shift
                </span>
                <span className="text-sm font-bold text-foreground">
                  {Number(tempDelta) > 0 ? `+${Number(tempDelta).toFixed(1)}` : Number(tempDelta).toFixed(1)}°C
                </span>
              </div>
              <input
                type="range"
                min="-5"
                max="10"
                step="0.5"
                value={tempDelta}
                onChange={(event) => setTempDelta(event.target.value)}
                className="w-full accent-emerald-600"
              />
              <p className="text-[11px] text-muted-foreground">
                {Number(tempDelta) > 1.5
                  ? 'Simulating intense heatwave'
                  : Number(tempDelta) > 0
                  ? 'Simulating mild warming'
                  : 'Historical temperature baseline'}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <Button
              onClick={handleAnalyze}
              disabled={loading}
              size="lg"
              className="w-full rounded-full py-6 text-base font-semibold shadow-lg shadow-primary/20 transition-all hover:scale-[1.01]"
            >
              {loading ? (
                <>
                  <LoaderCircle className="mr-2 size-5 animate-spin" />
                  Evaluating 706 District Models...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 size-5" />
                  Run Crop Optimization
                </>
              )}
            </Button>
          </div>

          {error && (
            <div className="mt-4 flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200">
              <AlertCircle className="mt-0.5 size-4 shrink-0" />
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Foliar Vision Engine (Under Construction Card) */}
        <div className="rounded-[2rem] border border-amber-500/30 bg-card/90 p-6 shadow-xl shadow-amber-900/5 dark:shadow-black/20">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="rounded-full bg-amber-500/10 p-3 text-amber-600 dark:text-amber-400">
                <Leaf className="size-5" />
              </div>
              <div>
                <p className="text-base font-bold text-foreground">Foliar Vision Engine</p>
                <p className="text-xs text-muted-foreground">
                  Automated disease classification from leaf photography.
                </p>
              </div>
            </div>
            <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-400">
              🚧 Under Construction
            </span>
          </div>

          <div className="mt-4 rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-50/60 via-amber-50/20 to-orange-50/30 p-4 text-center dark:from-amber-950/20 dark:via-slate-900 dark:to-orange-950/20">
            <p className="text-xs text-muted-foreground">
              This module is undergoing model retraining and benchmark recalibration. Leaf image uploads are temporarily paused.
            </p>
          </div>
        </div>
      </div>

      {/* Right Column: Optimization Results & Multi-Dimensional Matrix */}
      <div className="space-y-6">
        {/* KPI Summary Cards */}
        <div className="grid gap-3 sm:grid-cols-2">
          <MetricCard
            icon={MapPinned}
            label="Location & Season"
            value={response ? `${response.district}` : district}
            helper={response ? `${response.season} Season` : `${season} Season`}
          />
          <MetricCard
            icon={Sprout}
            label="Top Recommendation"
            value={topCrop ? topCrop.crop : 'Awaiting Run'}
            helper={topCrop ? `Score: ${topCrop.composite_score.toFixed(3)} (${topCrop.risk_level} risk)` : 'Configure & run'}
          />
          <MetricCard
            icon={TrendingUp}
            label="Composite Average"
            value={recommendations.length ? averageScore.toFixed(3) : '—'}
            helper="Multi-criteria index (0.0 - 1.0)"
          />
          <MetricCard
            icon={CloudSun}
            label="Target Acreage"
            value={`${response ? response.area_hectares : area} ha`}
            helper={`Scenario: ${response?.scenario_applied ?? 'Baseline'}`}
          />
        </div>

        {/* Results Container with View Tabs */}
        <div className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/50 pb-4">
            <div>
              <p className="text-lg font-bold text-foreground">Optimization Dashboard</p>
              <p className="text-xs text-muted-foreground">
                Multi-criteria synthesis across yield, pricing, and ecological factors.
              </p>
            </div>

            {/* View Switcher Tabs */}
            {response && (
              <div className="flex rounded-full border border-border bg-secondary/60 p-1 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveTab('advisory')}
                  className={cn(
                    'flex items-center gap-1.5 rounded-full px-3 py-1 font-semibold transition',
                    activeTab === 'advisory'
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                >
                  <Sprout className="size-3.5" />
                  Ranked Crops
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('sustainability')}
                  className={cn(
                    'flex items-center gap-1.5 rounded-full px-3 py-1 font-semibold transition',
                    activeTab === 'sustainability'
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                >
                  <Droplet className="size-3.5" />
                  Sustainability
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('economics')}
                  className={cn(
                    'flex items-center gap-1.5 rounded-full px-3 py-1 font-semibold transition',
                    activeTab === 'economics'
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                >
                  <Coins className="size-3.5" />
                  Economics
                </button>
              </div>
            )}
          </div>

          <div className="mt-5">
            {!response && (
              <div className="flex min-h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-border/70 p-8 text-center">
                <div className="rounded-full bg-primary/10 p-4 text-primary">
                  <Sprout className="size-8" />
                </div>
                <p className="mt-4 text-base font-bold text-foreground">Ready for Crop Optimization</p>
                <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                  Select your district, season, and acreage on the left and click &quot;Run Crop Optimization&quot; to inspect ML recommendations.
                </p>
              </div>
            )}

            {/* TAB 1: RANKED ADVISORY */}
            {response && activeTab === 'advisory' && (
              <div className="space-y-4">
                {recommendations.map((item) => {
                  const isTop = item.rank === 1;
                  const sus = item.sustainability_metrics;

                  return (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      key={`${item.rank}-${item.crop}`}
                      className={cn(
                        'rounded-2xl border p-5 transition-all',
                        isTop
                          ? 'border-primary/50 bg-primary/5 shadow-md shadow-primary/5 dark:bg-primary/10'
                          : 'border-border/60 bg-background/60 hover:border-border'
                      )}
                    >
                      {/* Top Row */}
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <span
                            className={cn(
                              'flex size-8 items-center justify-center rounded-full text-xs font-bold',
                              isTop
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-muted-foreground'
                            )}
                          >
                            #{item.rank}
                          </span>
                          <div>
                            <h4 className="text-xl font-bold text-foreground">{item.crop}</h4>
                            <p className="text-xs text-muted-foreground">
                              Projected Revenue: <strong className="text-foreground">₹{Math.round(item.total_revenue_inr).toLocaleString()}</strong>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <span
                            className={cn(
                              'rounded-full px-3 py-1 text-xs font-semibold capitalize',
                              item.risk_level === 'low'
                                ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                                : item.risk_level === 'medium'
                                ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400'
                                : 'bg-rose-500/10 text-rose-700 dark:text-rose-400'
                            )}
                          >
                            {item.risk_level} Risk
                          </span>
                          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
                            Score {item.composite_score.toFixed(3)}
                          </span>
                        </div>
                      </div>

                      {/* Score Progress Bar */}
                      <div className="mt-3">
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-emerald-400 transition-all duration-500"
                            style={{ width: `${Math.min(item.composite_score * 100, 100)}%` }}
                          />
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
                        <MiniStat label="Predicted Yield" value={`${item.predicted_yield_tonnes_per_ha.toFixed(2)} t/ha`} />
                        <MiniStat label="Forecasted Price" value={`₹${Math.round(item.predicted_price_inr_per_tonne).toLocaleString()}/t`} />
                        <MiniStat label="Revenue / Ha" value={`₹${Math.round(item.expected_revenue_inr_per_ha).toLocaleString()}`} />
                        <MiniStat
                          label="Water Saved"
                          value={sus ? `${sus.water_saved_vs_baseline.toFixed(0)}%` : '—'}
                          highlight={Boolean(sus && sus.water_saved_vs_baseline > 0)}
                        />
                      </div>

                      {/* Sustainability Mini Footer */}
                      {sus && (
                        <div className="mt-3 flex flex-wrap items-center gap-3 border-t border-border/40 pt-3 text-[11px] text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Droplet className="size-3 text-sky-500" />
                            <span>Water: <strong className="text-foreground">{sus.water_use_estimate.toFixed(0)} index-ha</strong></span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Layers className="size-3 text-emerald-500" />
                            <span>Fertilizer Proxy: <strong className="text-foreground">{sus.fertilizer_proxy.toFixed(3)}</strong></span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Leaf className="size-3 text-lime-600" />
                            <span>Eco Score: <strong className="text-foreground">{sus.sustainability_score.toFixed(3)}</strong></span>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            )}

            {/* TAB 2: SUSTAINABILITY MATRIX */}
            {response && activeTab === 'sustainability' && (
              <div className="space-y-4">
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <p className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                    Deterministic FAO Agronomic Proxy Analysis
                  </p>
                  <p className="mt-1 text-[11px] text-muted-foreground">
                    Estimated water savings and ecological chemical intensity calculated against regional crop baselines.
                  </p>
                </div>

                {recommendations.map((item) => {
                  const sus = item.sustainability_metrics;
                  if (!sus) return null;

                  return (
                    <div
                      key={`sus-${item.crop}`}
                      className="rounded-2xl border border-border/60 bg-background/60 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="flex size-6 items-center justify-center rounded-full bg-secondary text-xs font-bold text-foreground">
                            #{item.rank}
                          </span>
                          <span className="font-bold text-foreground">{item.crop}</span>
                        </div>
                        <span className={cn(
                          'rounded-full px-2.5 py-0.5 text-xs font-semibold',
                          sus.water_saved_vs_baseline > 0
                            ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                            : 'bg-secondary text-muted-foreground'
                        )}>
                          {sus.water_saved_vs_baseline > 0 ? `+${sus.water_saved_vs_baseline.toFixed(0)}% Water Saved` : `${sus.water_saved_vs_baseline.toFixed(0)}% vs Baseline`}
                        </span>
                      </div>

                      <div className="mt-3 grid grid-cols-3 gap-2">
                        <MiniStat label="Water Use" value={`${sus.water_use_estimate.toFixed(0)} index-ha`} />
                        <MiniStat label="Fertilizer Proxy" value={sus.fertilizer_proxy.toFixed(3)} />
                        <MiniStat label="Carbon Proxy" value={`${sus.carbon_proxy.toFixed(1)} idx-ha`} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* TAB 3: ECONOMICS COMPARISON */}
            {response && activeTab === 'economics' && (
              <div className="space-y-4">
                <div className="rounded-xl border border-primary/20 bg-primary/5 p-4">
                  <p className="text-xs font-bold text-foreground">
                    Projected Revenue Distribution ({area} Hectares)
                  </p>
                  <p className="mt-1 text-[11px] text-muted-foreground">
                    Expected gross earnings based on forecasted wholesale mandi prices.
                  </p>
                </div>

                {recommendations.map((item) => {
                  const revenueRatio = (item.total_revenue_inr / maxRevenue) * 100;

                  return (
                    <div
                      key={`econ-${item.crop}`}
                      className="rounded-2xl border border-border/60 bg-background/60 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-foreground">{item.crop}</span>
                        <span className="text-sm font-bold text-primary">
                          ₹{Math.round(item.total_revenue_inr).toLocaleString()}
                        </span>
                      </div>

                      <div className="mt-2">
                        <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                          <div
                            className="h-full bg-primary transition-all duration-500"
                            style={{ width: `${Math.max(revenueRatio, 5)}%` }}
                          />
                        </div>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                        <span>Rate: ₹{Math.round(item.predicted_price_inr_per_tonne).toLocaleString()}/tonne</span>
                        <span>Yield: {item.predicted_yield_tonnes_per_ha.toFixed(2)} t/ha</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Methodology Disclaimers */}
        {response && (
          <div className="rounded-2xl border border-border/60 bg-card/60 p-5 text-xs leading-relaxed text-muted-foreground shadow-sm">
            <div className="flex items-start gap-2.5">
              <Info className="mt-0.5 size-4 shrink-0 text-primary" />
              <div>
                <p className="font-semibold text-foreground">Regulatory & Methodology Disclosure</p>
                <p className="mt-1">{response.disclaimer}</p>
                {response.sustainability_disclosure && (
                  <p className="mt-2 text-[11px] text-muted-foreground/90">{response.sustainability_disclosure}</p>
                )}
              </div>
            </div>
          </div>
        )}
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
    <div className="rounded-[1.75rem] border border-border/60 bg-card/90 p-5 shadow-lg shadow-lime-900/5 dark:shadow-black/20">
      <div className="flex items-center justify-between">
        <Icon className="size-5 text-primary" />
        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Metric</span>
      </div>
      <p className="mt-3 text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-bold tracking-tight text-foreground">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{helper}</p>
    </div>
  );
}

function MiniStat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="rounded-xl bg-secondary/50 p-2.5">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className={cn('mt-1 text-sm font-bold', highlight ? 'text-emerald-600 dark:text-emerald-400' : 'text-foreground')}>
        {value}
      </p>
    </div>
  );
}
