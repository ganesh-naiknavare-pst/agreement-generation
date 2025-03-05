import { useEffect } from "react";
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

export const useAgreements = () => {
  const { data, loading, error, fetchData } = useApi<Agreement[]>(BackendEndpoints.GetAgreements);

  useEffect(() => {
    fetchData({ method: "GET" });
  }, []);

  return { agreements: data, loading, error, fetchAgreements:fetchData };
};
