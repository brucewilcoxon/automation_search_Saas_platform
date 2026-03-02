import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center bg-background">
      <div className="h-14 w-14 rounded-full bg-secondary flex items-center justify-center mb-6">
        <MapPin className="h-7 w-7 text-muted-foreground" />
      </div>
      <h1 className="text-2xl font-bold text-foreground mb-2">Page not found</h1>
      <p className="text-sm text-muted-foreground max-w-sm mb-6">
        The page you're looking for doesn't exist or has been moved. Check the URL or head back to the dashboard.
      </p>
      <Button asChild>
        <Link to="/">Back to Dashboard</Link>
      </Button>
    </div>
  );
};

export default NotFound;
