select BaseModelStoragePrefix, Locale, Created, Id, Purposes from [dbo].[SpeechModels]
where BaseModelStoragePrefix like '0_zh-cn-batch-s2s-gpu-display_vadchange_beam3%'

update [dbo].[SpeechModels]
set Purposes = 'SyncTranscription'
where BaseModelStoragePrefix = '0_zh-cn-batch-s2s-gpu-display-20250927-1-1'

select BaseModelStoragePrefix, Locale, Created, Id, Purposes from [dbo].[SpeechModels]
where BaseModelStoragePrefix = '0_zh-cn-batch-s2s-gpu-display-20250927-1-1'

select top 20
    m.Locale, m.Id as 'Speech Model Id', d.Id as 'Model Deployment Id',
    m.BaseModelStoragePrefix, d.State, m.Created as ModelCreated,
    m.Purposes, d.IsManagedByGoalStateEngine, m.UsesDynamicGrammar
from [dbo].[ModelDeployments] d
join [dbo].[SpeechModels] as m on d.SpeechModelId = m.Id
-- where d.Id='f3be8589-5761-4f1b-86f7-5a4a8eb87308'
where m.BaseModelStoragePrefix like '%0_und-phi-v0-gpu-%'
order by m.Created desc

-- declare @modelId varchar(64)
-- declare @deployId varchar(64)
-- set @modelId='f28fc8c4-301c-4a5e-8dd1-518c542b168c'
-- set @deployId='62cf2cf5-6b9d-46db-a2ce-a9a30da89939'
-- delete from [dbo].[GoalStateModelOperationTasks] where GoalStateModelOperationId in (select Id from [dbo].[GoalStateModelOperations] where SpeechModelId=@modelId)
-- delete from [dbo].[GoalStateModelOperations] where SpeechModelId=@modelId
-- delete from [dbo].[ModelDeployments] where Id=@deployId
-- delete from [dbo].[BaseModelLocaleMappings] where SpeechModelId=@modelId
-- delete from [dbo].[SpeechModels] where Id=@modelId

select * from BaseModelLocaleMappings where SpeechModelId='f28fc8c4-301c-4a5e-8dd1-518c542b168c'


-- declare @deployId varchar(64)
-- set @deployId='62cf2cf5-6b9d-46db-a2ce-a9a30da89939'
-- delete from [dbo].[ModelDeployments] where Id=@deployId

select BaseModelStoragePrefix, Locale, Created, Id, Purposes, UsesDynamicGrammar from [dbo].[SpeechModels]
-- where BaseModelStoragePrefix like '%phi%'
where BaseModelStoragePrefix like '%0_und-phi-v0-gpu-%'
order by Created desc
