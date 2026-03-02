import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Search, Users, Phone, Mail } from "lucide-react";
import { motion } from "framer-motion";
import { api, type CashBuyer } from "@/lib/api";
import { EmptyState } from "@/components/EmptyState";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  Tooltip, TooltipContent, TooltipTrigger,
} from "@/components/ui/tooltip";

const CashBuyersPage = () => {
  const [searchParams] = useSearchParams();
  const [buyers, setBuyers] = useState<CashBuyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState(
    searchParams.get("county") || ""
  );

  useEffect(() => {
    api.getCashBuyers().then((data) => {
      setBuyers(data);
      setLoading(false);
    });
  }, []);

  const filtered = buyers.filter((b) =>
    `${b.name} ${b.company} ${b.county} ${b.state}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Cash Buyers</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Verified buyers who have closed land deals in your target markets. Use this list for direct outreach or to validate demand.
        </p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter by name, company, or county…"
          className="pl-9 bg-secondary border-0"
        />
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="rounded-lg border border-border bg-card">
        {loading ? (
          <div className="p-4 space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-8 flex-1" />
                <Skeleton className="h-8 w-32" />
                <Skeleton className="h-8 w-28" />
                <Skeleton className="h-8 w-16" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No buyers match your search"
            description="Try a different name, company, or county to find active cash buyers in your area."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="text-xs">Name</TableHead>
                <TableHead className="text-xs">Company</TableHead>
                <TableHead className="text-xs">Location</TableHead>
                <TableHead className="text-xs text-right">Deals</TableHead>
                <TableHead className="text-xs text-right">Last Active</TableHead>
                <TableHead className="text-xs text-right">Contact</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((buyer) => (
                <TableRow key={buyer.id} className="hover:bg-secondary/50">
                  <TableCell className="text-sm font-medium">{buyer.name}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{buyer.company}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{buyer.county}, {buyer.state}</TableCell>
                  <TableCell className="text-sm text-right font-mono">{buyer.totalPurchases}</TableCell>
                  <TableCell className="text-sm text-right text-muted-foreground">{new Date(buyer.lastActive).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <a href={`tel:${buyer.phone}`} className="inline-flex items-center justify-center h-7 w-7 rounded-md hover:bg-secondary transition-colors">
                            <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                          </a>
                        </TooltipTrigger>
                        <TooltipContent className="text-xs">{buyer.phone}</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <a href={`mailto:${buyer.email}`} className="inline-flex items-center justify-center h-7 w-7 rounded-md hover:bg-secondary transition-colors">
                            <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                          </a>
                        </TooltipTrigger>
                        <TooltipContent className="text-xs">{buyer.email}</TooltipContent>
                      </Tooltip>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </motion.div>
    </div>
  );
};

export default CashBuyersPage;
