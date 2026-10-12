import { BuildingInputProvider } from "@/providers/BuildingInputProvider";
import { QueryProvider } from "@/providers/QueryProvider";
import { ReferenceDataProvider } from "@/providers/ReferenceDataProvider";

// The providers load reference data from the API before rendering, so they wrap only the tool:
// the landing and legal pages must render without the API.
export default function ToolLayout({ children }: LayoutProps<"/tool">) {
  return (
    <QueryProvider>
      <ReferenceDataProvider>
        <BuildingInputProvider>{children}</BuildingInputProvider>
      </ReferenceDataProvider>
    </QueryProvider>
  );
}
