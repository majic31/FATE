ALTER TABLE t_task ADD f_is_deepspeed BOOL NOT NULL DEFAULT FALSE;
ALTER TABLE t_task ADD f_deepspeed_id VARCHAR(200) DEFAULT "";