import { observable, action, makeObservable, runInAction } from "mobx";
// types
import { IAppConfig } from "types/app";
// services
import { AppConfigService } from "services/app_config.service";

export interface IAppConfigStore {
  envConfig: IAppConfig | null;
  // action
  fetchAppConfig: () => Promise<any>;
}

export class AppConfigStore implements IAppConfigStore {
  // observables
  envConfig: IAppConfig | null = null;
  // service
  appConfigService;

  constructor() {
    makeObservable(this, {
      // observables
      envConfig: observable.ref,
      // actions
      fetchAppConfig: action,
    });
    this.appConfigService = new AppConfigService();
  }

  fetchAppConfig = async () => {
    try {
      const config = await this.appConfigService.envConfig();
      runInAction(() => {
        this.envConfig = config;
      });
      return config;
    } catch (error) {
      throw error;
    }
  };
}