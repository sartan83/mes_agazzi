package com.qcadoo.mes.basic;

import java.util.Collection;

import org.quartz.CronTrigger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.config.AbstractFactoryBean;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

@Component
public class TriggersFactoryBean extends AbstractFactoryBean<Collection<CronTrigger>> {

    @Autowired
    private ApplicationContext appContext;

    @Override
    public Class<?> getObjectType() {
        return Collection.class;
    }

    @Override
    protected Collection<CronTrigger> createInstance() throws Exception {
        return appContext.getBeansOfType(CronTrigger.class).values();
    }
}
