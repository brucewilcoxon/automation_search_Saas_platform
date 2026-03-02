import { Settings, Key, Bell, User } from "lucide-react";
import { Separator } from "@/components/ui/separator";

const SettingsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your account, API credentials, and notification preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { icon: User, title: "Account", description: "Profile details, email, and password." },
          { icon: Key, title: "API Keys", description: "Manage keys for external data sources." },
          { icon: Bell, title: "Notifications", description: "Configure alert rules and delivery channels." },
        ].map(({ icon: Icon, title, description }) => (
          <div
            key={title}
            className="rounded-lg border border-border bg-card p-5 space-y-2 opacity-60"
          >
            <div className="h-9 w-9 rounded-md bg-secondary flex items-center justify-center">
              <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            <p className="text-xs text-muted-foreground">{description}</p>
            <p className="text-[11px] text-muted-foreground/60 italic">Available in a future release.</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SettingsPage;
