import { useSearchParams } from "react-router-dom";
import { Mail, FileText, Send } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";

const LettersPage = () => {
  const [searchParams] = useSearchParams();
  const parcelId = searchParams.get("parcelId");
  const apn = searchParams.get("apn");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Letters</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Create and manage offer letters for land parcels. Letters are pre-filled with parcel and owner data when available.
        </p>
      </div>

      {parcelId && apn ? (
        <div className="rounded-lg border border-border bg-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Send className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">New Letter Campaign</h2>
          </div>
          <div className="rounded-md bg-secondary p-4 text-sm space-y-1">
            <p className="text-muted-foreground">
              Parcel: <span className="font-mono text-foreground">{apn}</span>
            </p>
            <p className="text-muted-foreground">
              County: <span className="text-foreground">{searchParams.get("county")}, {searchParams.get("state")}</span>
            </p>
          </div>
          <p className="text-xs text-muted-foreground">
            Letter template editor and PDF export will be available in a future update. Parcel fields above will auto-populate into the template.
          </p>
          <Button variant="outline" size="sm" disabled className="gap-2">
            <FileText className="h-3.5 w-3.5" />
            Generate Letter (Coming Soon)
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-card">
          <EmptyState
            icon={Mail}
            title="No letters yet"
            description="To start a letter campaign, visit a parcel detail page and click 'Create Letter Campaign.' The parcel data will be pre-filled for you."
            action={
              <Button variant="outline" size="sm" asChild>
                <a href="/search">
                  <FileText className="h-3.5 w-3.5 mr-2" />
                  Find Parcels
                </a>
              </Button>
            }
          />
        </div>
      )}
    </div>
  );
};

export default LettersPage;
