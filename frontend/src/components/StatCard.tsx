import { type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  change?: string;
  positive?: boolean;
}

export function StatCard({ label, value, icon: Icon, change, positive }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg border border-border bg-card p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</span>
        <div className="h-8 w-8 rounded-md bg-secondary flex items-center justify-center">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
      </div>
      <div className="text-2xl font-bold text-foreground tracking-tight">{value}</div>
      {change && (
        <p className={`text-xs mt-1 ${positive ? "text-success" : "text-destructive"}`}>
          {change}
        </p>
      )}
    </motion.div>
  );
}
