import { useState } from "react";
import { Search, Bell } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

export function AppHeader() {
  const [searchValue, setSearchValue] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchValue.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchValue.trim())}`);
      setSearchValue("");
    }
  };

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-border bg-background/80 backdrop-blur-sm px-4">
      <SidebarTrigger className="text-muted-foreground hover:text-foreground" />

      <form onSubmit={handleSearch} className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="Search by Parcel ID, APN, or address…"
            className="pl-9 h-9 bg-secondary border-0 text-sm placeholder:text-muted-foreground/60 focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>
      </form>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
            <Bell className="h-4 w-4" />
            <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-primary text-[10px] font-bold text-primary-foreground flex items-center justify-center">
              3
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-80">
          <div className="px-3 py-2 border-b border-border">
            <p className="text-sm font-semibold">Notifications</p>
          </div>
          <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
            <span className="text-sm">New auction found in Maricopa County</span>
            <span className="text-xs text-muted-foreground">2 minutes ago</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
            <span className="text-sm">Ingestion run completed — 234 parcels</span>
            <span className="text-xs text-muted-foreground">12 minutes ago</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
            <span className="text-sm">Harris County run has 2 errors</span>
            <span className="text-xs text-muted-foreground">38 minutes ago</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-xs font-semibold text-secondary-foreground">
        JD
      </div>
    </header>
  );
}
