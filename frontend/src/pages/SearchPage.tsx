import { useEffect, useState, useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search as SearchIcon,
  Filter,
  MapPin,
  Calendar,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import {
  api,
  type AuctionEvent,
  type AuctionEventFilters,
  FLORIDA_COUNTIES,
  US_STATES,
} from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { TableSkeleton } from "@/components/DataSkeleton";
import { EmptyState } from "@/components/EmptyState";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
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
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";

const ITEMS_PER_PAGE = 10;

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [events, setEvents] = useState<AuctionEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Filter state — default to Florida
  const [state, setState] = useState(searchParams.get("state") || "FL");
  const [county, setCounty] = useState(searchParams.get("county") || "all");
  const [status, setStatus] = useState(searchParams.get("status") || "all");
  const [dateFrom, setDateFrom] = useState<Date | undefined>();
  const [dateTo, setDateTo] = useState<Date | undefined>();
  const [minBid, setMinBid] = useState("");
  const [maxBid, setMaxBid] = useState("");
  const [parcelId, setParcelId] = useState("");

  const counties = useMemo(() => {
    if (state === "FL") return FLORIDA_COUNTIES;
    // For non-FL, derive from US_STATES or return empty
    return [];
  }, [state]);

  const fetchEvents = () => {
    setLoading(true);
    setPage(1);
    const filters: AuctionEventFilters = {
      state: state || undefined,
      county: county !== "all" ? county : undefined,
      status: status !== "all" ? status : undefined,
      dateFrom: dateFrom ? format(dateFrom, "yyyy-MM-dd") : undefined,
      dateTo: dateTo ? format(dateTo, "yyyy-MM-dd") : undefined,
      minBid: minBid ? Number(minBid) : undefined,
      maxBid: maxBid ? Number(maxBid) : undefined,
      parcelId: parcelId || undefined,
    };
    api.getAuctionEvents(filters).then((data) => {
      setEvents(data);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleApplyFilters = () => {
    fetchEvents();
    setMobileFiltersOpen(false);
  };

  const handleResetFilters = () => {
    setState("FL");
    setCounty("all");
    setStatus("all");
    setDateFrom(undefined);
    setDateTo(undefined);
    setMinBid("");
    setMaxBid("");
    setParcelId("");
    setPage(1);
    setLoading(true);
    api.getAuctionEvents({ state: "FL" }).then((data) => {
      setEvents(data);
      setLoading(false);
    });
  };

  // Pagination
  const totalPages = Math.max(1, Math.ceil(events.length / ITEMS_PER_PAGE));
  const paginatedEvents = events.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

  const activeFilterCount = [
    state !== "FL" ? state : null,
    county !== "all" ? county : null,
    status !== "all" ? status : null,
    dateFrom,
    dateTo,
    minBid,
    maxBid,
    parcelId,
  ].filter(Boolean).length;

  const filterPanel = (
    <div className="space-y-5">
      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          State
        </Label>
        <Select value={state} onValueChange={(v) => { setState(v); setCounty("all"); }}>
          <SelectTrigger className="bg-secondary border-0 h-9 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {US_STATES.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {counties.length > 0 && (
        <div className="space-y-1.5">
          <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            County
          </Label>
          <Select value={county} onValueChange={setCounty}>
            <SelectTrigger className="bg-secondary border-0 h-9 text-sm">
              <SelectValue placeholder="All counties" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All counties</SelectItem>
              {counties.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Status
        </Label>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="bg-secondary border-0 h-9 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="upcoming">Upcoming</SelectItem>
            <SelectItem value="live">Live</SelectItem>
            <SelectItem value="ended">Ended</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator className="bg-border" />

      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Date range
        </Label>
        <div className="grid grid-cols-2 gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "h-9 bg-secondary border-0 text-sm justify-start font-normal",
                  !dateFrom && "text-muted-foreground"
                )}
              >
                <Calendar className="h-3.5 w-3.5 mr-1.5 shrink-0" />
                {dateFrom ? format(dateFrom, "MM/dd") : "From"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <CalendarComponent
                mode="single"
                selected={dateFrom}
                onSelect={setDateFrom}
                initialFocus
                className="p-3 pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "h-9 bg-secondary border-0 text-sm justify-start font-normal",
                  !dateTo && "text-muted-foreground"
                )}
              >
                <Calendar className="h-3.5 w-3.5 mr-1.5 shrink-0" />
                {dateTo ? format(dateTo, "MM/dd") : "To"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <CalendarComponent
                mode="single"
                selected={dateTo}
                onSelect={setDateTo}
                initialFocus
                className="p-3 pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      <Separator className="bg-border" />

      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Bid range
        </Label>
        <div className="grid grid-cols-2 gap-2">
          <Input
            value={minBid}
            onChange={(e) => setMinBid(e.target.value)}
            placeholder="Min $"
            type="number"
            className="h-9 bg-secondary border-0 text-sm"
          />
          <Input
            value={maxBid}
            onChange={(e) => setMaxBid(e.target.value)}
            placeholder="Max $"
            type="number"
            className="h-9 bg-secondary border-0 text-sm"
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Parcel ID
        </Label>
        <Input
          value={parcelId}
          onChange={(e) => setParcelId(e.target.value)}
          placeholder="e.g. 123-45-678"
          className="h-9 bg-secondary border-0 text-sm font-mono"
        />
      </div>

      <div className="flex gap-2 pt-2">
        <Button onClick={handleApplyFilters} size="sm" className="flex-1 h-9">
          Apply Filters
        </Button>
        <Button
          onClick={handleResetFilters}
          variant="ghost"
          size="sm"
          className="h-9 text-muted-foreground"
        >
          Reset
        </Button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">
            Auction Search
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse tax deed auctions across Florida and beyond. Defaults to FL
            — adjust filters to explore other states.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="lg:hidden flex items-center gap-1.5"
          onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
        >
          <SlidersHorizontal className="h-4 w-4" />
          Filters
          {activeFilterCount > 0 && (
            <span className="ml-1 text-xs bg-primary text-primary-foreground rounded-full h-5 w-5 flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </Button>
      </div>

      <div className="flex gap-6">
        {/* Desktop filter panel */}
        <aside className="hidden lg:block w-64 shrink-0">
          <div className="sticky top-6 rounded-lg border border-border bg-card p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                Filters
              </h2>
              {activeFilterCount > 0 && (
                <span className="text-xs text-muted-foreground">
                  {activeFilterCount} active
                </span>
              )}
            </div>
            {filterPanel}
          </div>
        </aside>

        {/* Mobile filter panel */}
        <AnimatePresence>
          {mobileFiltersOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
            >
              <motion.div
                initial={{ x: "100%" }}
                animate={{ x: 0 }}
                exit={{ x: "100%" }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
                className="absolute right-0 top-0 h-full w-80 bg-card border-l border-border p-5 overflow-auto"
              >
                <div className="flex items-center justify-between mb-5">
                  <h2 className="text-sm font-semibold text-foreground">Filters</h2>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setMobileFiltersOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                {filterPanel}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <div className="flex-1 min-w-0">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-lg border border-border bg-card"
          >
            {loading ? (
              <div className="p-4">
                <TableSkeleton rows={8} cols={5} />
              </div>
            ) : events.length === 0 ? (
              <EmptyState
                icon={MapPin}
                title="No auctions match your criteria"
                description="Try broadening your search — remove date or county filters, or switch to a different state."
                action={
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleResetFilters}
                    className="mt-2"
                  >
                    Reset all filters
                  </Button>
                }
              />
            ) : (
              <>
                {/* Results header */}
                <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">
                    Showing{" "}
                    <span className="text-foreground font-medium">
                      {(page - 1) * ITEMS_PER_PAGE + 1}–
                      {Math.min(page * ITEMS_PER_PAGE, events.length)}
                    </span>{" "}
                    of{" "}
                    <span className="text-foreground font-medium">
                      {events.length}
                    </span>{" "}
                    auctions
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Page {page} of {totalPages}
                  </p>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="text-xs">Event Date</TableHead>
                      <TableHead className="text-xs">County</TableHead>
                      <TableHead className="text-xs">State</TableHead>
                      <TableHead className="text-xs text-right">
                        Items
                      </TableHead>
                      <TableHead className="text-xs text-right">
                        Status
                      </TableHead>
                      <TableHead className="text-xs text-right">
                        Action
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedEvents.map((evt, i) => (
                      <motion.tr
                        key={evt.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.025 }}
                        className="border-b border-border hover:bg-secondary/50 transition-colors"
                      >
                        <TableCell className="text-sm font-medium">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                            {format(new Date(evt.eventDate), "MMM d, yyyy")}
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          <Link
                            to={`/auction/${evt.id}`}
                            className="text-foreground hover:text-primary transition-colors font-medium"
                          >
                            {evt.county}
                          </Link>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {evt.state}
                        </TableCell>
                        <TableCell className="text-sm text-right font-mono">
                          {evt.itemCount.toLocaleString()}
                        </TableCell>
                        <TableCell className="text-right">
                          <StatusBadge status={evt.status} />
                        </TableCell>
                        <TableCell className="text-right">
                          <Link to={`/auction/${evt.id}`}>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 text-xs gap-1 text-muted-foreground hover:text-foreground"
                            >
                              View
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </Link>
                        </TableCell>
                      </motion.tr>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="px-4 py-3 border-t border-border flex items-center justify-between">
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => p - 1)}
                      className="h-8 text-xs gap-1"
                    >
                      <ChevronLeft className="h-3.5 w-3.5" />
                      Previous
                    </Button>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                        (p) => (
                          <button
                            key={p}
                            onClick={() => setPage(p)}
                            className={cn(
                              "h-8 w-8 rounded-md text-xs font-medium transition-colors",
                              p === page
                                ? "bg-primary text-primary-foreground"
                                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                            )}
                          >
                            {p}
                          </button>
                        )
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={page >= totalPages}
                      onClick={() => setPage((p) => p + 1)}
                      className="h-8 text-xs gap-1"
                    >
                      Next
                      <ChevronRight className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                )}
              </>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
