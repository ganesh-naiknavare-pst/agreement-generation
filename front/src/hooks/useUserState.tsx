import {
  createContext,
  useContext,
  ReactNode,
  useEffect,
  useState,
} from "react";
import useApi, { BackendEndpoints } from "./useApi";
import { useParams, useSearchParams } from "react-router-dom";
export type UserData = {
  id: number;
  userId: string;
  agreementId: number;
  status: string;
};

interface UserContextType {
  rentAgreementUser: UserData | null;
  getRentAgreementUser: (method: {}) => Promise<void>;
  TemplateAgreementUser: UserData | null;
  getTemplateAgreementUser: (method: {}) => Promise<void>;
  setStatus: React.Dispatch<React.SetStateAction<string | null>>;
  status: string | null;
}

const UserContext = createContext<UserContextType>({
  rentAgreementUser: null,
  getRentAgreementUser: () => Promise.resolve(),
  TemplateAgreementUser: null,
  getTemplateAgreementUser: () => Promise.resolve(),
  setStatus: () => {},
  status: null,
});

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const { data: rentAgreementUser, fetchData: getRentAgreementUser } =
    useApi<UserData>(BackendEndpoints.GetRentAgreementUser);
  const { data: TemplateAgreementUser, fetchData: getTemplateAgreementUser } =
    useApi<UserData>(BackendEndpoints.GetTemplateAgreementUSer);
  const param = useParams();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (param.id && param.agreementId) {
      const requestData = {
        agreement_id: param.agreementId,
        user_id: param.id,
      };
      if (searchParams.get("type") === "rent") {
        getRentAgreementUser({ method: "GET", params: requestData });
        if (rentAgreementUser) {
          setStatus(rentAgreementUser.status);
        }
      } else {
        getTemplateAgreementUser({ method: "GET", params: requestData });
        if (TemplateAgreementUser) {
          setStatus(TemplateAgreementUser.status);
        }
      }
    }
  }, []);

  return (
    <UserContext.Provider
      value={{
        rentAgreementUser,
        getRentAgreementUser,
        TemplateAgreementUser,
        getTemplateAgreementUser,
        setStatus,
        status,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUserState = () => useContext(UserContext);
