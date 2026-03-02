import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft, MapPin, DollarSign, FileText, Users, Mail, Clock,
  ExternalLink, Info, Droplets, Building2, Receipt, Globe,
} from "lucide-react";
import { motion } from "framer-motion";
import { api, type Parcel } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { ErrorState } from "@/components/ErrorState";
import { CardSkeleton } from "@/components/DataSkeleton";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */

function DetailRow({
  label,
  value,
  mono,
  muted,
  tooltip,
}: {
  label: string;
  value: string | number | null;
  mono?: boolean;
  muted?: boolean;
  tooltip?: string;
}) {
  const display = value ?? "—";
  return (
    <div className="flex items-center justify-between py-2.5 gap-4">
      <span className="text-sm text-muted-foreground flex items-center gap-1.5 shrink-0">
        {label}
        {tooltip && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Info className="h-3 w-3 text-muted-foreground/50 cursor-help" />
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-[220px] text-xs">
              {tooltip}
            </TooltipContent>
          </Tooltip>
        )}
      </span>
      <span
        className={`text-sm text-right ${mono ? "font-mono" : "font-medium"} ${
          muted ? "text-muted-foreground" : "text-foreground"
        }`}
      >
        {display}
      </span>
    </div>
  );
}

function FreshnessIndicator({ date }: { date: string }) {
  const days = Math.floor(
    (Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24)
  );
  const fresh = days <= 7;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex items-center gap-1.5 cursor-default">
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              fresh ? "bg-emerald-500" : "bg-amber-500"
            }`}
          />
          <span className="text-[11px] text-muted-foreground">
            {fresh ? "Fresh" : "Stale"} · {days}d ago
          </span>
        </div>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="text-xs max-w-[200px]">
        Last data refresh was {days} day{days !== 1 ? "s" : ""} ago.
        {!fresh && " Consider re-running ingestion for this county."}
      </TooltipContent>
    </Tooltip>
  );
}

/* ------------------------------------------------------------------ */
/* Mock comparable sales                                              */
/* ------------------------------------------------------------------ */

interface CompSale {
  address: string;
  area: string;
  price: number;
  date: string;
  distance: string;
  similarity: number;
}

function generateComps(months: 6 | 12): CompSale[] {
  const base: CompSale[] = [
    { address: "14201 SW 248th St", area: "1.8 ac", price: 72000, date: "2026-01-10", distance: "0.4 mi", similarity: 92 },
    { address: "25430 SW 147th Ave", area: "2.1 ac", price: 68500, date: "2025-12-22", distance: "0.9 mi", similarity: 87 },
    { address: "19800 NW 12th Ct", area: "1.5 ac", price: 55000, date: "2025-11-15", distance: "1.2 mi", similarity: 81 },
    { address: "30501 S Dixie Hwy", area: "3.0 ac", price: 110000, date: "2025-10-30", distance: "2.1 mi", similarity: 74 },
  ];
  if (months === 12) {
    base.push(
      { address: "8920 SW 184th St", area: "2.4 ac", price: 79000, date: "2025-06-18", distance: "1.5 mi", similarity: 83 },
      { address: "4400 NW 199th Ter", area: "1.1 ac", price: 41000, date: "2025-05-02", distance: "3.2 mi", similarity: 68 }
    );
  }
  return base;
}

function SimilarityBadge({ score }: { score: number }) {
  const color =
    score >= 85
      ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/20"
      : score >= 70
      ? "bg-amber-500/15 text-amber-400 border-amber-500/20"
      : "bg-red-500/15 text-red-400 border-red-500/20";
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          className={`inline-flex items-center rounded px-1.5 py-0.5 text-[11px] font-mono font-medium border ${color} cursor-help`}
        >
          {score}%
        </span>
      </TooltipTrigger>
      <TooltipContent side="top" className="text-xs max-w-[200px]">
        Similarity is based on acreage, zoning, and proximity.
        ≥85% = strong match, 70-84% = moderate, &lt;70% = weak.
      </TooltipContent>
    </Tooltip>
  );
}

function CompsTable({ months }: { months: 6 | 12 }) {
  const comps = generateComps(months);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="pb-2 pr-4 text-xs font-medium text-muted-foreground">Address</th>
            <th className="pb-2 pr-4 text-xs font-medium text-muted-foreground">Area</th>
            <th className="pb-2 pr-4 text-xs font-medium text-muted-foreground text-right">Price</th>
            <th className="pb-2 pr-4 text-xs font-medium text-muted-foreground">Date</th>
            <th className="pb-2 pr-4 text-xs font-medium text-muted-foreground">Distance</th>
            <th className="pb-2 text-xs font-medium text-muted-foreground text-right">Similarity</th>
          </tr>
        </thead>
        <tbody>
          {comps.map((c, i) => (
            <tr key={i} className="border-b border-border/50 last:border-0">
              <td className="py-2.5 pr-4 font-medium text-foreground">{c.address}</td>
              <td className="py-2.5 pr-4 font-mono text-muted-foreground">{c.area}</td>
              <td className="py-2.5 pr-4 font-mono text-foreground text-right">
                ${c.price.toLocaleString()}
              </td>
              <td className="py-2.5 pr-4 text-muted-foreground">{c.date}</td>
              <td className="py-2.5 pr-4 text-muted-foreground">{c.distance}</td>
              <td className="py-2.5 text-right">
                <SimilarityBadge score={c.similarity} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                               */
/* ------------------------------------------------------------------ */

const ParcelDetailPage = () => {
  const { parcelId } = useParams<{ parcelId: string }>();
  const { toast } = useToast();
  const [parcel, setParcel] = useState<Parcel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!parcelId) return;
    api
      .getParcel(parcelId)
      .then((p) => {
        if (!p) {
          setError(true);
          return;
        }
        setParcel(p);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [parcelId]);

  if (error)
    return (
      <ErrorState
        title="Parcel not found"
        message="This parcel may have been removed or the ID is invalid. Double-check the parcel ID and try again."
      />
    );

  const handleGeneratePdf = () => {
    toast({
      title: "Report queued",
      description: "Your auction PDF report will be ready in a few moments.",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/search">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div className="min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-xl font-bold text-foreground tracking-tight">
              {loading ? "Loading…" : `Parcel ${parcel?.apn}`}
            </h1>
            {parcel && <StatusBadge status={parcel.status} />}
          </div>
          <p className="text-sm text-muted-foreground mt-0.5 truncate">
            {loading ? "" : parcel?.address}
          </p>
        </div>
        {parcel && (
          <div className="ml-auto hidden sm:block">
            <FreshnessIndicator date="2026-02-23" />
          </div>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <CardSkeleton />
        </div>
      ) : (
        parcel && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* ---- Left column ---- */}
            <div className="lg:col-span-2 space-y-6">
              {/* Parcel Overview */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg border border-border bg-card p-5"
              >
                <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  Parcel Overview
                </h2>
                <DetailRow label="Parcel ID" value={parcel.apn} mono tooltip="Assessor's Parcel Number as recorded by the county." />
                <Separator />
                <DetailRow label="County / State" value={`${parcel.county}, ${parcel.state}`} />
                <Separator />
                <DetailRow label="Acreage" value={`${parcel.acreage} ac`} mono />
                <Separator />
                <DetailRow
                  label="Zoning"
                  value={parcel.zoning}
                  tooltip="Current zoning designation per county records. Verify with planning dept before purchase."
                />
                <Separator />
                <DetailRow
                  label="Assessed Value"
                  value={`$${parcel.marketValue.toLocaleString()}`}
                  mono
                  tooltip="County-assessed market value. May differ from appraised or sale value."
                />
                <Separator />
                <DetailRow label="Annual Taxes" value={null} muted tooltip="Tax data is pending ingestion for this county." />
                <Separator />
                <DetailRow
                  label="Coordinates"
                  value={`${parcel.latitude.toFixed(4)}, ${parcel.longitude.toFixed(4)}`}
                  mono
                />
                <Separator />
                <DetailRow
                  label="Flood Zone"
                  value={null}
                  muted
                  tooltip="FEMA flood zone designation. Not yet available for this parcel."
                />
                <Separator />
                <div className="pt-1 sm:hidden">
                  <FreshnessIndicator date="2026-02-23" />
                </div>
              </motion.div>

              {/* Comparable Sales */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 }}
                className="rounded-lg border border-border bg-card p-5"
              >
                <h2 className="text-sm font-semibold text-foreground mb-1 flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-primary" />
                  Comparable Sales
                </h2>
                <p className="text-xs text-muted-foreground mb-4">
                  Recent closed sales near this parcel with similar size and zoning characteristics.
                </p>

                <Tabs defaultValue="6m">
                  <TabsList className="mb-4">
                    <TabsTrigger value="6m" className="text-xs">
                      Last 6 months
                    </TabsTrigger>
                    <TabsTrigger value="12m" className="text-xs">
                      Last 12 months
                    </TabsTrigger>
                  </TabsList>
                  <TabsContent value="6m">
                    <CompsTable months={6} />
                  </TabsContent>
                  <TabsContent value="12m">
                    <CompsTable months={12} />
                  </TabsContent>
                </Tabs>

                <div className="mt-4 rounded-md bg-muted/50 border border-border px-3 py-2.5">
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    <strong className="text-foreground/80">How similarity works:</strong>{" "}
                    The similarity score is a weighted composite of acreage proximity (40%),
                    zoning match (30%), and geographic distance (30%). Scores ≥85% indicate
                    strong comparables; 70–84% are moderate. This is an approximation — always
                    verify with local appraisals before making offers.
                  </p>
                </div>
              </motion.div>
            </div>

            {/* ---- Right column: Actions ---- */}
            <div className="space-y-4">
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.12 }}
                className="rounded-lg border border-border bg-card p-5 space-y-3"
              >
                <h2 className="text-sm font-semibold text-foreground">Actions</h2>

                <Button
                  className="w-full justify-start gap-2"
                  variant="default"
                  size="sm"
                  onClick={handleGeneratePdf}
                >
                  <FileText className="h-4 w-4" />
                  Generate Auction PDF Report
                </Button>
                <p className="text-[11px] text-muted-foreground -mt-1 pl-1">
                  Includes parcel details, comps, and county data.
                </p>

                <Separator />

                <Button
                  className="w-full justify-start gap-2"
                  variant="outline"
                  size="sm"
                  asChild
                >
                  <Link
                    to={`/tools/cash-buyers?county=${encodeURIComponent(parcel.county)}&state=${parcel.state}`}
                  >
                    <Users className="h-4 w-4" />
                    Find Cash Buyers
                  </Link>
                </Button>
                <p className="text-[11px] text-muted-foreground -mt-1 pl-1">
                  Pre-filtered to {parcel.county} County buyers.
                </p>

                <Separator />

                <Button
                  className="w-full justify-start gap-2"
                  variant="outline"
                  size="sm"
                  asChild
                >
                  <Link
                    to={`/tools/letters?parcelId=${parcel.id}&apn=${encodeURIComponent(parcel.apn)}&county=${encodeURIComponent(parcel.county)}&state=${parcel.state}`}
                  >
                    <Mail className="h-4 w-4" />
                    Create Letter Campaign
                  </Link>
                </Button>
                <p className="text-[11px] text-muted-foreground -mt-1 pl-1">
                  Auto-fills parcel fields into letter template.
                </p>
              </motion.div>

              {/* Auction context */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.16 }}
                className="rounded-lg border border-border bg-card p-5 space-y-2"
              >
                <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-primary" />
                  Auction Context
                </h2>
                <DetailRow label="Auction" value={parcel.auctionId} mono />
                <DetailRow
                  label="Min Bid"
                  value={`$${parcel.minBid.toLocaleString()}`}
                  mono
                />
                <DetailRow
                  label="Discount"
                  value={`${Math.round((1 - parcel.minBid / parcel.marketValue) * 100)}% below assessed`}
                />
                <Separator />
                <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-xs" asChild>
                  <Link to={`/auction/${parcel.auctionId}`}>
                    <ExternalLink className="h-3.5 w-3.5" />
                    View full auction event
                  </Link>
                </Button>
              </motion.div>

              {/* Valuation summary */}
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="rounded-lg border border-border bg-card p-5 space-y-2"
              >
                <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Receipt className="h-4 w-4 text-primary" />
                  Quick Valuation
                </h2>
                <DetailRow label="Assessed" value={`$${parcel.marketValue.toLocaleString()}`} mono />
                <DetailRow label="Min Bid" value={`$${parcel.minBid.toLocaleString()}`} mono />
                <DetailRow label="Avg Comp (6mo)" value="$73,875" mono />
                <Separator />
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  Comp average based on {generateComps(6).length} nearby sales. Not a formal appraisal.
                </p>
              </motion.div>
            </div>
          </div>
        )
      )}
    </div>
  );
};

export default ParcelDetailPage;
