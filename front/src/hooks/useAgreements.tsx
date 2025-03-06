import { createContext, useContext, ReactNode, useEffect } from "react";
import useApi, { BackendEndpoints } from "./useApi";

export interface Agreement {
  id: number;
  address: string;
  city: string;
  startDate: string;
  pdf: string;
  owner: {
    name: string;
    email: string;
  }[];
  tenants: {
    name: string;
    email: string;
  }[];
  status: string;
}

export interface TemplateAgreement {
  id: number;
  address: string;
  city: string;
  createdAt: string;
  pdf: string;
  authority: {
    email: string;
  }[];
  participant: {
    email: string;
  }[];
  status: string;
}

interface AgreementContextType {
  agreements: Agreement[] | null;
  loadRentAgreemnts: boolean;
  fetchAgreements: () => Promise<void>;
  templateAgreement: TemplateAgreement[] | null;
  loadTemplatetAgreemnts: boolean;
  fetchTemplateAgreements: () => Promise<void>;
}

const AgreementsContext = createContext<AgreementContextType>({
  agreements: [],
  loadRentAgreemnts: false,
  fetchAgreements: () => Promise.resolve(),
  templateAgreement: [],
  loadTemplatetAgreemnts: false,
  fetchTemplateAgreements: () => Promise.resolve(),
});

export const AgreementsProvider = ({ children }: { children: ReactNode }) => {
  const {
    data: agreements,
    loading: loadRentAgreemnts,
    fetchData: fetchAgreements,
  } = useApi<Agreement[]>(BackendEndpoints.GetAgreements);
  const {
    data: templateAgreement,
    loading: loadTemplatetAgreemnts,
    fetchData: fetchTemplateAgreements,
  } = useApi<TemplateAgreement[]>(BackendEndpoints.GetTemplateAgreements);

  useEffect(() => {
    fetchAgreements({ method: "GET" });
    fetchTemplateAgreements({ method: "GET" });
  }, []);

  return (
    <AgreementsContext.Provider
      value={{
        agreements,
        loadRentAgreemnts,
        fetchAgreements,
        templateAgreement,
        loadTemplatetAgreemnts,
        fetchTemplateAgreements,
      }}
    >
      {children}
    </AgreementsContext.Provider>
  );
};

export const useAgreements = () => useContext(AgreementsContext);
