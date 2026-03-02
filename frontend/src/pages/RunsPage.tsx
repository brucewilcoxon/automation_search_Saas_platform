import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Activity, Play, Clock, AlertCircle, CheckCircle2,
  XCircle, RotateCcw, ChevronRight, Terminal, Loader2,
} from "lucide-react";
import { api, type IngestionRun, FLORIDA_COUNTIES, US_STATES } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

/* ------------------------------------------------------------------ */
/* Mock log lines                                                     */
/* ------------------------------------------------------------------ */

function generateMockLogs(run: IngestionRun): string[] {
  const lines = [
    `[INFO]  Starting ingestion for ${run.source}`,
    `[INFO]  Connecting to auction source…`,
    `[INFO]  Session established — fetching listing pages`,
    `[INFO]  Found ${run.parcelsTotal} parcels to process`,
  ];
  if (run.parcelsProcessed > 0) {
    lines.push(`[INFO]  Processed ${run.parcelsProcessed} of ${run.parcelsTotal} parcels`);
  }
  if (run.errors > 0) {
    lines.push(`[ERROR] ${run.errors} parcels failed validation — see error details below`);
    lines.push(`[ERROR] Parcel "UNKNOWN-001": Missing required field "apn"`);
    if (run.errors > 1) {
      lines.push(`[ERROR] Parcel "UNKNOWN-002": Geocode lookup timed out after 30s`);
    }
  }
  if (run.status === "completed") {
    lines.push(`[INFO]  Ingestion complete — ${run.parcelsProcessed} parcels written to database`);
    lines.push(`[INFO]  Duration: ${run.completedAt ? Math.round((new Date(run.completedAt).getTime() - new Date(run.startedAt).getTime()) / 1000) : 0}s`);
  }
  if (run.status === "failed") {
    lines.push(`[FATAL] Ingestion aborted — too many consecutive errors`);
    lines.push(`[INFO]  Partial data (${run.parcelsProcessed} parcels) has been saved`);
  }
  if (run.status === "running") {
    lines.push(`[INFO]  Still processing… ${run.parcelsTotal - run.parcelsProcessed} remaining`);
  }
  return lines;
}

/* ------------------------------------------------------------------ */
/* Page                                                               */
/* ------------------------------------------------------------------ */

const RunsPage = () => {
  const { toast } = useToast();
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState<IngestionRun | null>(null);

  // New run form
  const [triggerState, setTriggerState] = useState("FL");
  const [triggerCounty, setTriggerCounty] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.getIngestionRuns().then((data) => {
      setRuns(data);
      setLoading(false);
    });
  }, []);

  const handleTriggerRun = () => {
    if (!triggerCounty) {
      toast({ title: "Select a county", description: "Choose the county you want to ingest data from.", variant: "destructive" });
      return;
    }
    setSubmitting(true);
    // Simulate POST /ingest/run
    setTimeout(() => {
      const newRun: IngestionRun = {
        id: `run-${Date.now()}`,
        source: `${triggerCounty} County (${triggerState})`,
        status: "running",
        startedAt: new Date().toISOString(),
        completedAt: null,
        parcelsProcessed: 0,
        parcelsTotal: Math.floor(Math.random() * 300) + 50,
        errors: 0,
      };
      setRuns((prev) => [newRun, ...prev]);
      setSubmitting(false);
      setTriggerCounty("");
      toast({ title: "Ingestion started", description: `Now scraping ${triggerCounty} County, ${triggerState}.` });
    }, 800);
  };

  const handleRetry = (run: IngestionRun) => {
    toast({ title: "Retry queued", description: `Re-running ingestion for ${run.source}.` });
    setSelectedRun(null);
  };

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleString(undefined, {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle2 className="h-4 w-4 text-success" />;
      case "failed": return <XCircle className="h-4 w-4 text-destructive" />;
      case "running": return <Loader2 className="h-4 w-4 text-primary animate-spin" />;
      default: return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Ingestion Runs</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Monitor data pipelines and trigger new scraping jobs.
        </p>
      </div>

      {/* Trigger new run */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-lg border border-border bg-card p-5"
      >
        <h2 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
          <Play className="h-4 w-4 text-primary" />
          Run Ingestion
        </h2>
        <div className="flex flex-col sm:flex-row gap-3 items-end">
          <div className="space-y-1.5 flex-1 max-w-[180px]">
            <Label className="text-xs text-muted-foreground uppercase tracking-wider">State</Label>
            <Select value={triggerState} onValueChange={(v) => { setTriggerState(v); setTriggerCounty(""); }}>
              <SelectTrigger className="bg-secondary border-0 h-9 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {US_STATES.map((s) => (
                  <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5 flex-1 max-w-[220px]">
            <Label className="text-xs text-muted-foreground uppercase tracking-wider">County</Label>
            <Select value={triggerCounty} onValueChange={setTriggerCounty}>
              <SelectTrigger className="bg-secondary border-0 h-9 text-sm">
                <SelectValue placeholder="Select county…" />
              </SelectTrigger>
              <SelectContent>
                {(triggerState === "FL" ? FLORIDA_COUNTIES : ["Maricopa", "Harris", "Dallas", "Los Angeles", "Clark"]).map((c) => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleTriggerRun} disabled={submitting} size="sm" className="h-9 gap-2">
            {submitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            {submitting ? "Starting…" : "Start Run"}
          </Button>
        </div>
        <p className="text-[11px] text-muted-foreground mt-3">
          This will scrape the selected county's auction site and import all listed parcels. Typical runs take 2–15 minutes depending on listing volume.
        </p>
      </motion.div>

      {/* Runs table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.08 }}
        className="rounded-lg border border-border bg-card"
      >
        <div className="px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-foreground">Recent Runs</h2>
        </div>

        {loading ? (
          <div className="p-4 space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-8 flex-1" />
                <Skeleton className="h-8 w-28" />
                <Skeleton className="h-8 w-40" />
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-8 w-20" />
              </div>
            ))}
          </div>
        ) : runs.length === 0 ? (
          <EmptyState
            icon={Activity}
            title="No ingestion runs yet"
            description="Start your first run above to begin importing auction data."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="text-xs w-10"></TableHead>
                <TableHead className="text-xs">Source</TableHead>
                <TableHead className="text-xs">Started</TableHead>
                <TableHead className="text-xs">Finished</TableHead>
                <TableHead className="text-xs w-48">Progress</TableHead>
                <TableHead className="text-xs text-right">Errors</TableHead>
                <TableHead className="text-xs text-right">Status</TableHead>
                <TableHead className="text-xs w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => {
                const pct = run.parcelsTotal > 0
                  ? Math.round((run.parcelsProcessed / run.parcelsTotal) * 100)
                  : 0;
                const logs = generateMockLogs(run);
                const lastLog = logs[logs.length - 1];
                return (
                  <TableRow
                    key={run.id}
                    className="hover:bg-secondary/50 cursor-pointer group"
                    onClick={() => setSelectedRun(run)}
                  >
                    <TableCell className="text-center">
                      {getStatusIcon(run.status)}
                    </TableCell>
                    <TableCell>
                      <div>
                        <span className="text-sm font-medium text-foreground">{run.source}</span>
                        <p className="text-[11px] text-muted-foreground truncate max-w-[260px] mt-0.5 font-mono">
                          {lastLog}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                      {formatTime(run.startedAt)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                      {run.completedAt ? formatTime(run.completedAt) : "—"}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress value={pct} className="h-1.5 flex-1" />
                        <span className="text-xs font-mono text-muted-foreground w-12 text-right">
                          {run.parcelsProcessed}/{run.parcelsTotal}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className={`text-sm text-right font-mono ${run.errors > 0 ? "text-destructive" : "text-muted-foreground"}`}>
                      {run.errors}
                    </TableCell>
                    <TableCell className="text-right">
                      <StatusBadge status={run.status} />
                    </TableCell>
                    <TableCell className="text-right">
                      <ChevronRight className="h-4 w-4 text-muted-foreground/40 group-hover:text-muted-foreground transition-colors" />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </motion.div>

      {/* Run detail modal */}
      <Dialog open={!!selectedRun} onOpenChange={(open) => !open && setSelectedRun(null)}>
        {selectedRun && (
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-base">
                {getStatusIcon(selectedRun.status)}
                {selectedRun.source}
              </DialogTitle>
              <DialogDescription>
                Run ID: <span className="font-mono">{selectedRun.id}</span>
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {/* Meta */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground text-xs">Started</span>
                  <p className="font-medium">{formatTime(selectedRun.startedAt)}</p>
                </div>
                <div>
                  <span className="text-muted-foreground text-xs">Finished</span>
                  <p className="font-medium">{selectedRun.completedAt ? formatTime(selectedRun.completedAt) : "In progress"}</p>
                </div>
                <div>
                  <span className="text-muted-foreground text-xs">Parcels</span>
                  <p className="font-medium font-mono">{selectedRun.parcelsProcessed} / {selectedRun.parcelsTotal}</p>
                </div>
                <div>
                  <span className="text-muted-foreground text-xs">Errors</span>
                  <p className={`font-medium font-mono ${selectedRun.errors > 0 ? "text-destructive" : ""}`}>{selectedRun.errors}</p>
                </div>
              </div>

              <Separator />

              {/* Logs */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Terminal className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Logs</span>
                </div>
                <div className="bg-secondary rounded-md p-3 max-h-[200px] overflow-auto">
                  {generateMockLogs(selectedRun).map((line, i) => (
                    <p
                      key={i}
                      className={`text-[11px] font-mono leading-relaxed ${
                        line.includes("[ERROR]") || line.includes("[FATAL]")
                          ? "text-destructive"
                          : "text-muted-foreground"
                      }`}
                    >
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            </div>

            <DialogFooter className="gap-2">
              <Button variant="outline" size="sm" onClick={() => setSelectedRun(null)}>
                Close
              </Button>
              {selectedRun.status === "failed" && (
                <Button size="sm" className="gap-2" onClick={() => handleRetry(selectedRun)}>
                  <RotateCcw className="h-3.5 w-3.5" />
                  Retry Run
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
};

export default RunsPage;
