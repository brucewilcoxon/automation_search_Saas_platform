import { Search, Gavel, MapPin, Users, Mail, Activity, Settings, LayoutDashboard } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const mainNav = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Auction Search", url: "/search", icon: Search },
];

const toolsNav = [
  { title: "Cash Buyers", url: "/tools/cash-buyers", icon: Users },
  { title: "Letters", url: "/tools/letters", icon: Mail },
];

const systemNav = [
  { title: "Ingestion Runs", url: "/runs", icon: Activity },
  { title: "Settings", url: "/settings", icon: Settings },
];

function NavSection({ label, items }: { label: string; items: typeof mainNav }) {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";

  return (
    <SidebarGroup>
      {!collapsed && <SidebarGroupLabel className="text-[11px] uppercase tracking-wider text-muted-foreground/60 font-semibold">{label}</SidebarGroupLabel>}
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton asChild>
                <NavLink
                  to={item.url}
                  end={item.url === "/"}
                  className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
                  activeClassName="bg-sidebar-accent text-sidebar-accent-foreground"
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  {!collapsed && <span>{item.title}</span>}
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";

  return (
    <Sidebar collapsible="icon" className="border-r border-border">
      <div className={`flex items-center gap-2 px-4 py-4 ${collapsed ? "justify-center" : ""}`}>
        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
          <MapPin className="h-4 w-4 text-primary-foreground" />
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-bold text-foreground tracking-tight">LandScope</span>
            <span className="text-[10px] text-muted-foreground leading-none">Auction Intelligence</span>
          </div>
        )}
      </div>
      <SidebarContent className="px-2">
        <NavSection label="Main" items={mainNav} />
        <NavSection label="Tools" items={toolsNav} />
        <NavSection label="System" items={systemNav} />
      </SidebarContent>
    </Sidebar>
  );
}
