import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type StatusType = "upcoming" | "live" | "completed" | "ended" | "running" | "failed" | "available" | "sold" | "withdrawn" | "cancelled" | "pending";

const statusStyles: Record<StatusType, string> = {
  upcoming: "bg-info/15 text-info border-info/20",
  live: "bg-success/15 text-success border-success/20 animate-pulse-subtle",
  completed: "bg-muted text-muted-foreground border-border",
  ended: "bg-muted text-muted-foreground border-border",
  running: "bg-primary/15 text-primary border-primary/20 animate-pulse-subtle",
  failed: "bg-destructive/15 text-destructive border-destructive/20",
  available: "bg-success/15 text-success border-success/20",
  sold: "bg-muted text-muted-foreground border-border",
  withdrawn: "bg-warning/15 text-warning border-warning/20",
  cancelled: "bg-destructive/15 text-destructive border-destructive/20",
  pending: "bg-warning/15 text-warning border-warning/20",
};

export function StatusBadge({ status }: { status: StatusType }) {
  return (
    <Badge variant="outline" className={cn("text-[11px] font-medium capitalize", statusStyles[status])}>
      {status}
    </Badge>
  );
}
