from MLs.Trainer import Trainer

trainer = Trainer("complete_infected_data.log", "labels.log")
trainer.prepareAndTrain()