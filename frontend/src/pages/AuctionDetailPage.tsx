import { useEffect, useState, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  ExternalLink,
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Package,
  Link2,
  Hash,
} from "lucide-react";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { api, type AuctionEvent, type AuctionItem } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TableSkeleton } from "@/components/DataSkeleton";
import { ErrorState } from "@/components/ErrorState";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type SortKey = "parcelIdRaw" | "openingBid" | "status";
type SortDir = "asc" | "desc";

const ITEMS_PER_PAGE = 15;

const AuctionDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [event, setEvent] = useState<AuctionEvent | null>(null);
  const [items, setItems] = useState<AuctionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Filters & sort
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortKey, setSortKey] = useState<SortKey>("parcelIdRaw");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!id) return;
    Promise.all([api.getAuctionEvent(id), api.getAuctionItems(id)])
      .then(([evt, itms]) => {
        if (!evt) {
          setError(true);
          return;
        }
        setEvent(evt);
        setItems(itms);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(1);
  };

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column)
      return <ArrowUpDown className="h-3 w-3 text-muted-foreground/50" />;
    return sortDir === "asc" ? (
      <ArrowUp className="h-3 w-3 text-primary" />
    ) : (
      <ArrowDown className="h-3 w-3 text-primary" />
    );
  };

  const filtered = useMemo(() => {
    let result = [...items];

    // Text search
    if (query) {
      const q = query.toLowerCase();
      result = result.filter(
        (item) =>
          item.parcelIdRaw.toLowerCase().includes(q) ||
          item.parcelIdNorm.toLowerCase().includes(q)
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      result = result.filter((item) => item.status === statusFilter);
    }

    // Sort
    result.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "parcelIdRaw") {
        cmp = a.parcelIdRaw.localeCompare(b.parcelIdRaw);
      } else if (sortKey === "openingBid") {
        cmp = a.openingBid - b.openingBid;
      } else if (sortKey === "status") {
        cmp = a.status.localeCompare(b.status);
      }
      return sortDir === "asc" ? cmp : -cmp;
    });

    return result;
  }, [items, query, statusFilter, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const paginated = filtered.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [query, statusFilter]);

  if (error)
    return (
      <ErrorState
        title="Auction not found"
        message="This auction event may have been removed or the link is invalid."
      />
    );

  return (
    <div className="space-y-6">
      {/* Back nav + title */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild className="shrink-0">
          <Link to="/search">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div className="min-w-0">
          <h1 className="text-xl font-bold text-foreground tracking-tight truncate">
            {loading
              ? "Loading…"
              : `${event?.county} County, ${event?.state}`}
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Tax Deed Auction Event
          </p>
        </div>
        {event && (
          <div className="ml-auto shrink-0">
            <StatusBadge status={event.status} />
          </div>
        )}
      </div>

      {/* Summary card */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-20 rounded-lg bg-card border border-border animate-pulse"
            />
          ))}
        </div>
      ) : (
        event && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <SummaryCard
              icon={Calendar}
              label="Event Date"
              value={format(new Date(event.eventDate), "MMM d, yyyy")}
            />
            <SummaryCard
              icon={Hash}
              label="County"
              value={`${event.county}, ${event.state}`}
            />
            <SummaryCard
              icon={Package}
              label="Total Items"
              value={event.itemCount.toLocaleString()}
            />
            <div className="rounded-lg border border-border bg-card p-4 flex flex-col justify-between">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <Link2 className="h-3.5 w-3.5" />
                Source
              </div>
              <a
                href={event.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-primary hover:underline truncate flex items-center gap-1"
              >
                {new URL(event.sourceUrl).hostname}
                <ExternalLink className="h-3 w-3 shrink-0" />
              </a>
            </div>
          </div>
        )
      )}

      {/* Items table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-lg border border-border bg-card"
      >
        {/* Table toolbar */}
        <div className="px-4 py-3 border-b border-border flex flex-col sm:flex-row gap-3 sm:items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">
            Auction Items
          </h2>
          <div className="flex gap-2 flex-1 sm:max-w-md sm:justify-end">
            <div className="relative flex-1 sm:max-w-[220px]">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search parcel ID…"
                className="h-8 pl-8 bg-secondary border-0 text-sm font-mono"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-8 w-32 bg-secondary border-0 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All status</SelectItem>
                <SelectItem value="available">Available</SelectItem>
                <SelectItem value="sold">Sold</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {loading ? (
          <div className="p-4">
            <TableSkeleton rows={8} cols={6} />
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={Package}
            title="No items match"
            description={
              items.length === 0
                ? "This auction event doesn't have any items yet. Items are added as the auction date approaches."
                : "Try adjusting your search or status filter."
            }
            action={
              items.length > 0 ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setQuery("");
                    setStatusFilter("all");
                  }}
                >
                  Clear filters
                </Button>
              ) : undefined
            }
          />
        ) : (
          <>
            <div className="overflow-auto max-h-[600px]">
              <Table>
                <TableHeader className="sticky top-0 z-10 bg-card">
                  <TableRow className="hover:bg-transparent border-b border-border">
                    <TableHead className="text-xs w-12 text-center">
                      #
                    </TableHead>
                    <TableHead>
                      <button
                        onClick={() => handleSort("parcelIdRaw")}
                        className="flex items-center gap-1.5 text-xs font-medium hover:text-foreground transition-colors"
                      >
                        Parcel ID (Raw)
                        <SortIcon column="parcelIdRaw" />
                      </button>
                    </TableHead>
                    <TableHead className="text-xs">
                      Parcel ID (Normalized)
                    </TableHead>
                    <TableHead>
                      <button
                        onClick={() => handleSort("openingBid")}
                        className="flex items-center gap-1.5 text-xs font-medium hover:text-foreground transition-colors ml-auto"
                      >
                        Opening Bid
                        <SortIcon column="openingBid" />
                      </button>
                    </TableHead>
                    <TableHead>
                      <button
                        onClick={() => handleSort("status")}
                        className="flex items-center gap-1.5 text-xs font-medium hover:text-foreground transition-colors ml-auto"
                      >
                        Status
                        <SortIcon column="status" />
                      </button>
                    </TableHead>
                    <TableHead className="text-xs text-right">
                      Actions
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginated.map((item, i) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.02 }}
                      className="border-b border-border hover:bg-secondary/50 transition-colors"
                    >
                      <TableCell className="text-xs text-muted-foreground text-center font-mono">
                        {(page - 1) * ITEMS_PER_PAGE + i + 1}
                      </TableCell>
                      <TableCell className="text-sm font-mono font-medium text-foreground">
                        {item.parcelIdRaw}
                      </TableCell>
                      <TableCell className="text-sm font-mono text-muted-foreground">
                        {item.parcelIdNorm}
                      </TableCell>
                      <TableCell className="text-sm text-right font-mono">
                        ${item.openingBid.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <StatusBadge status={item.status} />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <a
                            href={item.itemUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 text-xs gap-1 text-muted-foreground hover:text-foreground"
                            >
                              Source
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </a>
                          <Link to={`/parcel/${item.parcelIdNorm}`}>
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-7 text-xs"
                            >
                              View Parcel
                            </Button>
                          </Link>
                        </div>
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 border-t border-border flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Showing{" "}
                <span className="text-foreground font-medium">
                  {(page - 1) * ITEMS_PER_PAGE + 1}–
                  {Math.min(page * ITEMS_PER_PAGE, filtered.length)}
                </span>{" "}
                of{" "}
                <span className="text-foreground font-medium">
                  {filtered.length}
                </span>{" "}
                items
              </p>
              {totalPages > 1 && (
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                    className="h-7 text-xs"
                  >
                    Previous
                  </Button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (p) => (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={cn(
                          "h-7 w-7 rounded-md text-xs font-medium transition-colors",
                          p === page
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                        )}
                      >
                        {p}
                      </button>
                    )
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => p + 1)}
                    className="h-7 text-xs"
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
};

function SummaryCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      <p className="text-sm font-semibold text-foreground">{value}</p>
    </div>
  );
}

export default AuctionDetailPage;
