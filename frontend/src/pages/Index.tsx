import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Gavel, MapPin, Activity, TrendingUp, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { api, type Auction, type IngestionRun } from "@/lib/api";
import { StatCard } from "@/components/StatCard";
import { StatusBadge } from "@/components/StatusBadge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const Index = () => {
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getAuctions(), api.getIngestionRuns()]).then(([a, r]) => {
      setAuctions(a);
      setRuns(r);
      setLoading(false);
    });
  }, []);

  const upcomingCount = auctions.filter((a) => a.status === "upcoming").length;
  const liveCount = auctions.filter((a) => a.status === "live").length;
  const totalParcels = auctions.reduce((sum, a) => sum + a.totalParcels, 0);
  const activeRuns = runs.filter((r) => r.status === "running").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">At-a-glance view of auction activity and data pipelines.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-lg border border-border bg-card p-4 space-y-3">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-8 w-1/2" />
              <Skeleton className="h-3 w-2/3" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Upcoming Auctions" value={upcomingCount} icon={Gavel} change="+2 this week" positive />
          <StatCard label="Live Now" value={liveCount} icon={TrendingUp} />
          <StatCard label="Total Parcels" value={totalParcels.toLocaleString()} icon={MapPin} change="+512 new" positive />
          <StatCard label="Active Runs" value={activeRuns} icon={Activity} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Auctions */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="rounded-lg border border-border bg-card">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">Upcoming Auctions</h2>
            <Button variant="ghost" size="sm" asChild className="text-xs text-muted-foreground hover:text-foreground">
              <Link to="/search">View all <ArrowRight className="h-3 w-3 ml-1" /></Link>
            </Button>
          </div>
          {loading ? (
            <div className="p-4 space-y-3">
              {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-xs">County</TableHead>
                  <TableHead className="text-xs">Date</TableHead>
                  <TableHead className="text-xs text-right">Parcels</TableHead>
                  <TableHead className="text-xs text-right">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auctions.slice(0, 5).map((auction) => (
                  <TableRow key={auction.id} className="hover:bg-secondary/50">
                    <TableCell className="text-sm font-medium">
                      <Link to={`/auction/${auction.id}`} className="hover:text-primary transition-colors">
                        {auction.county}, {auction.state}
                      </Link>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{new Date(auction.date).toLocaleDateString()}</TableCell>
                    <TableCell className="text-sm text-right font-mono">{auction.totalParcels}</TableCell>
                    <TableCell className="text-right"><StatusBadge status={auction.status} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </motion.div>

        {/* Recent Runs */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="rounded-lg border border-border bg-card">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">Data Pipelines</h2>
            <Button variant="ghost" size="sm" asChild className="text-xs text-muted-foreground hover:text-foreground">
              <Link to="/runs">View all <ArrowRight className="h-3 w-3 ml-1" /></Link>
            </Button>
          </div>
          {loading ? (
            <div className="p-4 space-y-3">
              {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-xs">Source</TableHead>
                  <TableHead className="text-xs w-36">Progress</TableHead>
                  <TableHead className="text-xs text-right">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.map((run) => {
                  const pct = run.parcelsTotal > 0 ? Math.round((run.parcelsProcessed / run.parcelsTotal) * 100) : 0;
                  return (
                    <TableRow key={run.id} className="hover:bg-secondary/50">
                      <TableCell className="text-sm font-medium">{run.source}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={pct} className="h-1.5 flex-1" />
                          <span className="text-xs font-mono text-muted-foreground">{pct}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right"><StatusBadge status={run.status} /></TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Index;
